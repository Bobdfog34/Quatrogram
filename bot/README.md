# Quatrogram registration bot

Distributes a unique phone number + 5-digit code to every user, verifies them
by Telegram ID and username, and reports successful registration back into chat.

## Modes

- **Local / VPS (current):** run `bot/bot.py` once; it polls with built-in retries. First locally, then on VPS.
- **GitHub Actions (optional):** a scheduled workflow can run the same script
  every few minutes.

## Secrets / environment

| Name | Required | Meaning |
| --- | --- | --- |
| `BOT_TOKEN` | yes | Telegram Bot API token. Never commit it. |
| `DATABASE_URL` | no | PostgreSQL connection string. If absent, a local `bot_state.db` SQLite file is used. |
| `ADMIN_IDS` | no | Comma-separated Telegram IDs allowed to use `/find` and `/confirm`. |
| `ADMIN_USERNAMES` | no | Comma-separated usernames (without `@`) allowed to use admin commands. Currently `VUral_Gaisin`. |
| `ADMIN_CHAT_IDS` | no | Numeric admin chats that receive registration reports. Admins are also learned automatically when they write to the bot. |
| `NUMBER_PREFIX` | no | Prefix for generated numbers, default `+7000`. Normalized to digits only for the server. |
| `CODE_TTL_MINUTES` | no | Code lifetime, default `5` (matches gramsrv `TELESRV_AUTH_CODE_TTL`). |
| `POLL_INTERVAL_SECONDS` | no | Retry delay after a network/database error, default `5`. |
| `SQLITE_PATH` | no | SQLite file path, default `bot_state.db`. |

## Commands

- `/start`, `/help` — instructions
- `/number` — issue a unique number and 5-digit code
- `/code` — show the current code
- `/status` — show number, code and registration state
- `/find @username` or `/find 123456789` — admin lookup by username or ID
- `/confirm @username` — fallback: mark registration as complete manually

A bare `@username` or numeric ID also performs a lookup for admins.

## Server integration (gramsrv)

The bot writes codes to `telegram_bot_registration_codes` — the same table that
the patched gramsrv reads. Phone numbers are normalized to digits only, matching
`domain.NormalizePhone` in gramsrv.

gramsrv side (see `docs/GRAMSVR_REGISTRATION_PATCH.md`):

1. At `auth.sendCode` / `auth.resendCode`, copy the active code from
   `telegram_bot_registration_codes` into Redis `store.PhoneCode.Code`.
2. Keep the existing Redis verifier unchanged.
3. After `auth.SignUp` succeeds, set `registered_at` and `user_id` in that table.
4. The bot polls `registered_at`, sends the user their ID and number, and sends
   an admin report with the Telegram ID, username and number.

Until the server patch is deployed, `/confirm` can simulate step 3.
