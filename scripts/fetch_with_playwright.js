#!/usr/bin/env node
const fs = require("fs");
const { URL } = require("url");

function loadPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_CORE_PATH) candidates.push(process.env.PLAYWRIGHT_CORE_PATH);
  candidates.push("playwright-core");
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (err) {
    }
  }
  throw new Error(
    "Unable to load playwright-core. Set PLAYWRIGHT_CORE_PATH or install playwright-core."
  );
}

function launchOptions(headless) {
  const options = { headless };
  if (process.env.PLAYWRIGHT_BROWSER_CHANNEL) {
    options.channel = process.env.PLAYWRIGHT_BROWSER_CHANNEL;
  }
  return options;
}

function userAgent() {
  return process.env.KOMODO_USER_AGENT ||
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36";
}

function findKomodoPage(context, origin) {
  const pages = context.pages();
  return pages.find((candidate) => candidate.url().startsWith(origin)) || pages[0] || null;
}

async function main() {
  const [, , targetUrl, outputPath] = process.argv;
  if (!targetUrl || !outputPath) {
    console.error("usage: fetch_with_playwright.js URL OUTPUT_PATH");
    process.exit(1);
  }

  const { chromium } = loadPlaywright();
  const headless = process.env.PLAYWRIGHT_HEADLESS !== "0";
  const profileDir = process.env.PLAYWRIGHT_PROFILE_DIR;
  const storageState = process.env.PLAYWRIGHT_STORAGE_STATE;
  const referer = process.env.PLAYWRIGHT_REFERER;
  const cdpEndpoint = process.env.PLAYWRIGHT_CDP_ENDPOINT;
  const fetchTimeoutMs = Number(process.env.PLAYWRIGHT_FETCH_TIMEOUT_MS || 20000);

  let browser = null;
  let context = null;
  let page = null;
  let shouldCloseBrowser = false;
  let shouldCloseContext = false;
  let shouldClosePage = false;

  if (cdpEndpoint) {
    browser = await chromium.connectOverCDP(cdpEndpoint);
    shouldCloseBrowser = true;
    context = browser.contexts()[0];
    if (!context) {
      throw new Error(`No browser context available via CDP endpoint ${cdpEndpoint}`);
    }
    const origin = new URL(targetUrl).origin + "/";
    page = findKomodoPage(context, origin);
    if (!page) {
      page = await context.newPage();
      shouldClosePage = true;
    }
  } else if (profileDir) {
    context = await chromium.launchPersistentContext(profileDir, {
      ...launchOptions(headless),
      userAgent: userAgent(),
    });
    shouldCloseContext = true;
    page = context.pages()[0] || await context.newPage();
  } else {
    browser = await chromium.launch(launchOptions(headless));
    shouldCloseBrowser = true;
    context = await browser.newContext({
      userAgent: userAgent(),
      storageState: storageState || undefined,
      extraHTTPHeaders: referer ? { Referer: referer } : undefined,
    });
    shouldCloseContext = true;
    page = await context.newPage();
  }

  try {
    const origin = new URL(targetUrl).origin + "/";
    if (!page.url().startsWith(origin)) {
      await page.goto(origin, { waitUntil: "domcontentloaded", timeout: 45000 });
    }
    const body = await page.evaluate(async ({ url, timeoutMs }) => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), timeoutMs);
      const response = await fetch(url, { credentials: "include", signal: controller.signal });
      clearTimeout(timeout);
      return await response.text();
    }, { url: targetUrl, timeoutMs: fetchTimeoutMs });
    fs.writeFileSync(outputPath, body);
  } finally {
    if (shouldClosePage && page && !page.isClosed()) {
      await page.close();
    }
    if (shouldCloseContext && context) {
      await context.close();
    }
    if (shouldCloseBrowser && browser) {
      await browser.close();
    }
  }
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
