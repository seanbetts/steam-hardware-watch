# Source Map

Use primary sources first.

## Komodo

- `https://komodostation.com/wp-json/`
- `https://komodostation.com/wp-json/wp/v2/product`
- `https://komodostation.com/wp-json/wp/v2/sections`
- `https://komodostation.com/wp-json/wp/v2/media`

Known product IDs from the seeded baseline:

- `Steam Controller JPY`: `413763`
- `Steam Machine JPY`: `413772`
- `Steam Frame JPY`: `413776`

Known section IDs from `2026-04-24` controller rollout:

- `433306` banner
- `433326` people video
- `433356` features
- `433376` video
- `433416` buttons
- `433434` custom
- `433470` features
- `433484` spec image

## SteamDB

- `Steam Controller app`: `https://steamdb.info/app/4165870/`
- `Steam Controller history`: `https://steamdb.info/app/4165870/history/`
- `Unboxing video app`: `https://steamdb.info/app/4653940/`
- `Unboxing video package`: `https://steamdb.info/sub/1620489/`

## SteamTracking / GameTracking

Primary local paths if already cloned:

- `/tmp/SteamTracking-master`
- `/tmp/GameTracking-*`

High-yield files from the seeded baseline:

- `ClientExtracted/steamui/localization/steamui_english.json`
- `Protobufs/webuimessages_steaminput.proto`
- `Protobufs/steammessages_clientsettings.proto`
- `steamcommunity.com/public/javascript/webui/friends.js`
- `Strings/steamclient.txt`

Useful search terms:

- `Triton`
- `Ibex`
- `Puck`
- `Steam Controller`
- `dock`
- `pair`
- `firmware`

## SteamVR Depots

SteamVR is Steam app `250820`.

- SteamDB depots page: `https://steamdb.info/app/250820/depots/`
- official news API: `https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=250820&count=40&maxlength=12000&format=json`

High-yield depots:

- `250821`: Windows OpenVR Win32
- `250823`: Linux OpenVR Linux
- `250824`: Windows/Linux OpenVR Content
- `250827`: Windows/Linux OpenVR Content 2
- `250830`: SteamVR Environments Content
- `250831`: SteamVR Environments Windows
- `250832`: SteamVR Environments Linux

Useful search terms:

- `Steam Frame`
- `Frame`
- `Deckard`
- `Roy`
- `Triton`
- `Ibex`
- `Puck`
- `Steam Link VR`
- `dongle`
- `activeFrame`
- `summonOverlayKey`
- `XR`
- `VR`

## SteamOS Package Mirror

- root mirror: `https://steamdeck-packages.steamos.cloud/archlinux-mirror/`
- source mirror: `https://steamdeck-packages.steamos.cloud/archlinux-mirror/sources/`

High-yield repos:

- `holo-main`
- `holo-3.8`
- `jupiter-main`
- `jupiter-3.8`
- `core-main`
- `extra-main`
- `multilib-main`

Useful search terms:

- `Fremont`
- `Deckard`
- `Steam Frame`
- `Roy`
- `Ibex`
- `Triton`
- `Lilac`
- `XR`
- `VR`
- `dongle`
- `firmware`
- `aarch64`
- `arm64`
- `qcom`
- `snapdragon`

## Valve Endpoints

Check for newly exposed assets or support flows:

- Steam support
- Steam store app pages
- linked manuals, PDFs, videos, and images
- `https://store.steampowered.com/app/4165870/`
- `https://help.steampowered.com/en/wizard/HelpWithSteamDeck`
- `https://www.steamdeck.com/`
- `https://steampowered.com/hardware`

## Customs / Regulatory

Run ImportInfo customs checks every normal watch run because they are quick and high-signal. Use customs data as corroborating evidence, not as primary proof.

- customs and import records
- ImportInfo automated search for CEVA/Valve: `https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION`
- ImportInfo automated search for Ingram/Valve: `https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION`
- ImportInfo automated search for Tech-Front game console Valve: `https://www.importinfo.com/search?s=TECH-FRONT%20GAME%20CONSOLE%20VALVE`
- ImportInfo automated search for Valve Corporation game console: `https://www.importinfo.com/search?s=VALVE%20CORPORATION%20GAME%20CONSOLE`
- ImportInfo manual/corroborating Tech-Front supplier page: `https://www.importinfo.com/tech-front-chongqing-computer-co`
- ImportInfo manual/corroborating Valve Corporation page: `https://www.importinfo.com/valve-corporation`
- NBD Valve Corporation public company page: `https://en.nbd.ltd/trader/info/NBDD3Y527621220`
- NBD buyer search for Valve Corporation: `https://en.nbd.ltd/customs-data?t=2&v=Valve%20Corporation`
- ImportGenius Ingram Micro C/O Valve Corporation page: `https://www.importgenius.cn/importers/ingram-micro-c-o-valve-corporation`
- HMRC UK Trade Info: rejected for this workflow because it is lagged monthly aggregate/trader data rather than shipment-level data.
- FCC
- Bluetooth SIG
- Wi-Fi Alliance

Do not elevate these above direct Komodo, SteamDB, or Valve evidence when those primary sources disagree.
