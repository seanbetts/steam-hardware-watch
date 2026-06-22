#!/usr/bin/env node
const fs = require("fs");
const { URL } = require("url");

function loadPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_CORE_PATH) candidates.push(process.env.PLAYWRIGHT_CORE_PATH);
  candidates.push("playwright-core");
  candidates.push("playwright");
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (err) {
    }
  }
  throw new Error(
    "Unable to load Playwright. Set PLAYWRIGHT_CORE_PATH, set NODE_PATH to a node_modules directory, or install playwright/playwright-core."
  );
}

function launchOptions(headless) {
  const options = { headless };
  const channel = process.env.STEAMDB_BROWSER_CHANNEL || process.env.PLAYWRIGHT_BROWSER_CHANNEL;
  if (channel) {
    options.channel = channel;
  }
  return options;
}

function userAgent() {
  return process.env.STEAMDB_USER_AGENT ||
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36";
}

function findPage(context, origin) {
  const pages = context.pages();
  return pages.find((candidate) => candidate.url().startsWith(origin)) || pages[0] || null;
}

async function main() {
  const [, , targetUrl, outputPath] = process.argv;
  if (!targetUrl || !outputPath) {
    console.error("usage: fetch_steamdb_with_playwright.js URL OUTPUT_PATH");
    process.exit(1);
  }

  const { chromium } = loadPlaywright();
  const headless = process.env.STEAMDB_PLAYWRIGHT_HEADLESS !== "0" &&
    process.env.PLAYWRIGHT_HEADLESS !== "0";
  const profileDir = process.env.STEAMDB_PROFILE_DIR || process.env.PLAYWRIGHT_PROFILE_DIR;
  const storageState = process.env.STEAMDB_STORAGE_STATE || process.env.PLAYWRIGHT_STORAGE_STATE;
  const referer = process.env.STEAMDB_REFERER || process.env.PLAYWRIGHT_REFERER;
  const cdpEndpoint = process.env.STEAMDB_CDP_ENDPOINT || process.env.PLAYWRIGHT_CDP_ENDPOINT;
  const settleMs = Number(process.env.STEAMDB_PLAYWRIGHT_SETTLE_MS || 8000);

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
    page = findPage(context, origin);
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
    await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
    if (settleMs > 0) {
      await page.waitForTimeout(settleMs);
    }
    fs.writeFileSync(outputPath, await page.content());
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
