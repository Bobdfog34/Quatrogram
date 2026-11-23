# Quatrogram

Telegram-compatible Android client for a self-hosted [gramsrv](https://github.com/iamxvbaba/gramsrv) server.

- **Declared app version:** 13.3.1
- **Upstream source baseline:** Telegram Android 13.2.2 (7303) — the newest source currently published in `TelegramMessenger/Telegram-Android`. Version 13.3.1 is set in `gradle.properties` because no public 13.3.1 source tree exists yet.
- **Server:** baked into the APK at build time. The client cannot switch datacenters or use Telegram's official network.
- **Build:** GitHub Actions. No local Android SDK required.

## Workflows

| Workflow | What it does |
|---|---|
| `Import Telegram source + Quatrogram patches` | Clones upstream Telegram Android with submodules, cherry-picks the gramsrv patches, applies the Quatrogram server lock / version / branding, and pushes the result to `master`. |
| `Build Quatrogram APK` | Builds `:TMessagesProj_App:assembleAfatRelease` and uploads the APK as an artifact. |

## Configuration

Set these as repository **Variables** (Settings → Secrets and variables → Actions → Variables), then re-run the import workflow:

| Variable | Default | Meaning |
|---|---|---|
| `SERVER_HOST` | `10.172.61.102` | MTProto host baked into the APK |
| `SERVER_PORT` | `2398` | MTProto port |
| `DC_ID` | `2` | Datacenter ID |
| `LINK_DOMAIN` | `quatrogram.net` | Domain used for public links |
| `SERVER_RSA_FINGERPRINT` | `0x9dbe5a4c45febeff` | Fingerprint of the bundled RSA key |
| `APP_DISPLAY_NAME` | `Quatrogram` | App label |

The RSA public key itself lives in `.github/config/server-rsa.pub`. Replace it together with `SERVER_RSA_FINGERPRINT` when using your own gramsrv identity.

## License

Based on Telegram Android (GPL-2.0-or-later) and gramsrv patches (GPL-2.0). Keep this repository public to comply with the licences. This project is unofficial and is not affiliated with Telegram.
