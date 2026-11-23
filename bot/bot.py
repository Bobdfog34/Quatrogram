#!/usr/bin/env python3
"""Quatrogram registration bot.

Polls Telegram Bot API updates, issues a unique phone number + code to each
user, and notifies them when gramsrv reports a successful registration.

The issued code is written to `telegram_bot_registration_codes`, the same table
that the patched gramsrv reads at auth.sendCode / auth.resendCode time. gramsrv
sets registered_at / user_id in that table after auth.SignUp succeeds.

State is stored in PostgreSQL when DATABASE_URL is set, otherwise in a local
SQLite file (handy for tests).
"""
import datetime as dt
import json
import os
import random
import re
import sqlite3
import sys
import time

import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
NUMBER_PREFIX = os.environ.get("NUMBER_PREFIX", "+7000").strip()
ADMIN_IDS = {x.strip() for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()}
ADMIN_USERNAMES = {
    x.strip().lstrip("@").lower()
    for x in os.environ.get("ADMIN_USERNAMES", "").split(",")
    if x.strip()
}
ADMIN_CHAT_IDS = {
    x.strip()
    for x in os.environ.get("ADMIN_CHAT_IDS", "").split(",")
    if x.strip()
}
CODE_TTL_MINUTES = int(os.environ.get("CODE_TTL_MINUTES", "5"))
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "5"))
API = "https://api.telegram.org/bot" + BOT_TOKEN
SQLITE_PATH = os.environ.get("SQLITE_PATH", "bot_state.db")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def expires_at():
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=CODE_TTL_MINUTES)).isoformat(timespec="seconds")


def normalize_phone(value):
    """Match gramsrv domain.NormalizePhone: digits only, no plus."""
    return re.sub(r"\D", "", value or "")


def pretty_phone(value):
    if not value:
        return "—"
    return value if value.startswith("+") else "+" + value


def is_expired(value):
    if not value:
        return True
    if isinstance(value, dt.datetime):
        expiry = value
    else:
        expiry = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=dt.timezone.utc)
    return expiry <= dt.datetime.now(dt.timezone.utc)


class Store:
    def __init__(self):
        self.pg = bool(DATABASE_URL)
        if self.pg:
            import psycopg2

            try:
                self.conn = psycopg2.connect(DATABASE_URL)
            except Exception as exc:
                # Local development: PostgreSQL may be stopped. Fall back to
                # SQLite instead of crashing the polling loop.
                print(f"PostgreSQL unavailable ({type(exc).__name__}), using SQLite", file=sys.stderr)
                self.pg = False
                self.conn = sqlite3.connect(SQLITE_PATH)
        else:
            self.conn = sqlite3.connect(SQLITE_PATH)
        self._init()

    def _sql(self, sql):
        return sql.replace("?", "%s") if self.pg else sql

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(self._sql(sql), params)
        self.conn.commit()
        return cur

    def query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(self._sql(sql), params)
        cols = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def _init(self):
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                tg_id BIGINT PRIMARY KEY,
                username TEXT,
                phone TEXT UNIQUE,
                code TEXT,
                status TEXT NOT NULL DEFAULT 'issued',
                notified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT,
                registered_at TEXT
            )
            """
        )
        # Adds admin notification state to databases created by older versions.
        try:
            self.execute("ALTER TABLE users ADD COLUMN admin_notified INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS numbers (
                phone TEXT PRIMARY KEY,
                assigned_to BIGINT,
                code TEXT,
                status TEXT NOT NULL DEFAULT 'issued',
                expires_at TEXT
            )
            """
        )
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        # This table is owned jointly with gramsrv. Use real timestamptz
        # columns on PostgreSQL so the server migration can coexist with it.
        if self.pg:
            self.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_bot_registration_codes (
                    phone varchar(32) PRIMARY KEY,
                    code varchar(10) NOT NULL,
                    issued_at timestamptz NOT NULL DEFAULT now(),
                    expires_at timestamptz NOT NULL,
                    claimed_at timestamptz,
                    registered_at timestamptz,
                    telegram_user_id bigint,
                    user_id bigint,
                    updated_at timestamptz NOT NULL DEFAULT now()
                )
                """
            )
        else:
            self.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_bot_registration_codes (
                    phone TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    issued_at TEXT,
                    expires_at TEXT,
                    claimed_at TEXT,
                    registered_at TEXT,
                    telegram_user_id INTEGER,
                    user_id INTEGER,
                    updated_at TEXT
                )
                """
            )

    def get_state(self, key, default=None):
        rows = self.query("SELECT value FROM state WHERE key=?", (key,))
        return rows[0]["value"] if rows else default

    def set_state(self, key, value):
        self.execute("DELETE FROM state WHERE key=?", (key,))
        self.execute("INSERT INTO state(key, value) VALUES(?, ?)", (key, str(value)))

    def ensure_user(self, tg_id, username):
        rows = self.query("SELECT tg_id FROM users WHERE tg_id=?", (tg_id,))
        if rows:
            self.execute("UPDATE users SET username=? WHERE tg_id=?", (username, tg_id))
        else:
            self.execute(
                "INSERT INTO users(tg_id, username, created_at) VALUES(?, ?, ?)",
                (tg_id, username, now()),
            )

    def user(self, tg_id):
        rows = self.query("SELECT * FROM users WHERE tg_id=?", (tg_id,))
        return rows[0] if rows else None

    def phone_taken(self, phone):
        return bool(
            self.query("SELECT 1 FROM users WHERE phone=?", (phone,))
            or self.query("SELECT 1 FROM numbers WHERE phone=?", (phone,))
        )

    def issue_number(self, tg_id):
        user = self.user(tg_id)
        if user and user.get("phone") and user.get("code"):
            reg = self.registration(row=user)
            if reg and reg.get("registered_at"):
                return user["phone"], user["code"], True
            if reg and not is_expired(reg.get("expires_at")):
                return user["phone"], user["code"], False
            # The old code has expired: reuse the same number with a fresh code.

        prefix = normalize_phone(NUMBER_PREFIX)
        if user and user.get("phone"):
            phone = user["phone"]
        else:
            for _ in range(200):
                phone = prefix + f"{random.randint(0, 999999):06d}"
                if not self.phone_taken(phone):
                    break
            else:
                raise RuntimeError("Не удалось найти свободный номер")

        code = f"{random.randint(0, 99999):05d}"
        stamp = now()
        expiry = expires_at()

        self.execute(
            "UPDATE users SET phone=?, code=?, status='issued', notified=0, registered_at=NULL WHERE tg_id=?",
            (phone, code, tg_id),
        )
        self.execute(
            "INSERT INTO numbers(phone, assigned_to, code, status, expires_at) VALUES(?, ?, ?, 'issued', ?) "
            "ON CONFLICT(phone) DO UPDATE SET assigned_to=excluded.assigned_to, code=excluded.code, "
            "status='issued', expires_at=excluded.expires_at"
            if self.pg else
            "INSERT OR REPLACE INTO numbers(phone, assigned_to, code, status, expires_at) VALUES(?, ?, ?, 'issued', ?)",
            (phone, tg_id, code, expiry),
        )
        self.upsert_code(phone, code, tg_id, stamp, expiry)
        return phone, code, False

    def upsert_code(self, phone, code, tg_id, stamp, expiry):
        """Publish the code for gramsrv to claim on auth.sendCode."""
        if self.pg:
            self.execute(
                "INSERT INTO telegram_bot_registration_codes "
                "(phone, code, issued_at, expires_at, claimed_at, registered_at, telegram_user_id, user_id, updated_at) "
                "VALUES(?, ?, ?, ?, NULL, NULL, ?, NULL, ?) "
                "ON CONFLICT(phone) DO UPDATE SET "
                "code=excluded.code, issued_at=excluded.issued_at, expires_at=excluded.expires_at, "
                "claimed_at=NULL, registered_at=NULL, telegram_user_id=excluded.telegram_user_id, "
                "user_id=NULL, updated_at=excluded.updated_at",
                (phone, code, stamp, expiry, tg_id, stamp),
            )
        else:
            self.execute(
                "INSERT OR REPLACE INTO telegram_bot_registration_codes "
                "(phone, code, issued_at, expires_at, claimed_at, registered_at, telegram_user_id, user_id, updated_at) "
                "VALUES(?, ?, ?, ?, NULL, NULL, ?, NULL, ?)",
                (phone, code, stamp, expiry, tg_id, stamp),
            )

    def registration(self, phone=None, row=None):
        """Return the gramsrv registration row for a phone (or bot user row)."""
        if phone is None and row is not None:
            phone = row.get("phone")
        if not phone:
            return None
        rows = self.query(
            "SELECT * FROM telegram_bot_registration_codes WHERE phone=?",
            (phone,),
        )
        return rows[0] if rows else None

    def mark_registered(self, phone, server_user_id=None):
        """Used by /confirm fallback and by status polling."""
        stamp = now()
        if self.pg:
            self.execute(
                "UPDATE telegram_bot_registration_codes "
                "SET registered_at=?, user_id=COALESCE(?, user_id), updated_at=? WHERE phone=?",
                (stamp, server_user_id, stamp, phone),
            )
        else:
            row = self.registration(phone)
            if row:
                self.execute(
                    "UPDATE telegram_bot_registration_codes "
                    "SET registered_at=?, user_id=COALESCE(?, user_id), updated_at=? WHERE phone=?",
                    (stamp, server_user_id, stamp, phone),
                )
        self.execute(
            "UPDATE users SET registered_at=?, status='registered', notified=0 WHERE phone=?",
            (stamp, phone),
        )
        self.execute("UPDATE numbers SET status='registered' WHERE phone=?", (phone,))

    def find(self, arg):
        a = arg.strip()
        if a.startswith("@"):
            return self.query("SELECT * FROM users WHERE username=?", (a[1:].lower(),))
        if a.isdigit():
            return self.query("SELECT * FROM users WHERE tg_id=?", (int(a),))
        low = a.lower()
        return self.query(
            "SELECT * FROM users WHERE lower(username)=? OR CAST(tg_id AS TEXT)=?",
            (low, a),
        )

    def confirm(self, rows):
        for row in rows:
            if row.get("phone"):
                self.mark_registered(row["phone"])

    def pending_notifications(self):
        return self.query(
            "SELECT u.tg_id, u.username, u.phone, u.code, u.admin_notified, "
            "c.registered_at, c.user_id "
            "FROM users u JOIN telegram_bot_registration_codes c ON c.phone=u.phone "
            "WHERE c.registered_at IS NOT NULL AND u.notified=0"
        )

    def pending_admin_notifications(self):
        return self.query(
            "SELECT u.tg_id, u.username, u.phone, c.registered_at, c.user_id "
            "FROM users u JOIN telegram_bot_registration_codes c ON c.phone=u.phone "
            "WHERE c.registered_at IS NOT NULL AND u.admin_notified=0"
        )

    def mark_notified(self, tg_id):
        self.execute("UPDATE users SET notified=1 WHERE tg_id=?", (tg_id,))

    def mark_admin_notified(self, tg_id):
        self.execute("UPDATE users SET admin_notified=1 WHERE tg_id=?", (tg_id,))


def api_call(method, payload=None, params=None):
    url = API + "/" + method
    if payload is not None:
        r = requests.post(url, json=payload, timeout=20)
    else:
        r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def send(chat_id, text):
    try:
        api_call(
            "sendMessage",
            payload={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
        )
    except Exception as exc:
        # Never print the token-containing URL from the exception.
        print(f"sendMessage failed for chat {chat_id}: {type(exc).__name__}", file=sys.stderr)


def is_admin(user_id, username):
    return (
        str(user_id) in ADMIN_IDS
        or (username or "").lower() in ADMIN_USERNAMES
    )


def remember_admin(store, tg_id, username):
    """Remember an admin's numeric chat id when they write to the bot."""
    if not is_admin(tg_id, username):
        return
    ADMIN_IDS.add(str(tg_id))
    ADMIN_CHAT_IDS.add(str(tg_id))
    try:
        known = set(json.loads(store.get_state("admin_chat_ids", "[]")))
    except (TypeError, ValueError):
        known = set()
    known.add(str(tg_id))
    store.set_state("admin_chat_ids", json.dumps(sorted(known, key=int)))


def all_admin_chat_ids(store):
    ids = set(ADMIN_CHAT_IDS)
    try:
        ids.update(json.loads(store.get_state("admin_chat_ids", "[]")))
    except (TypeError, ValueError):
        pass
    return sorted(ids, key=lambda x: int(x) if str(x).lstrip("-").isdigit() else 0)


def describe(store, row):
    phone = pretty_phone(row.get("phone"))
    code = row.get("code") or "—"
    reg = store.registration(row=row)
    if reg and reg.get("registered_at"):
        state = "зарегистрирован"
        if reg.get("user_id"):
            state += f" (server ID {reg['user_id']})"
    elif reg and reg.get("claimed_at"):
        state = "код принят сервером, ожидает ввода"
    else:
        state = "ожидает запроса кода в клиенте"
    uname = f"@{row['username']}" if row.get("username") else "—"
    return (
        f"ID: {row['tg_id']}\n"
        f"Юзернейм: {uname}\n"
        f"Номер: {phone}\n"
        f"Код: {code}\n"
        f"Статус: {state}"
    )


def handle(store, msg):
    text = (msg.get("text") or "").strip()
    if not text:
        return
    chat_id = msg["chat"]["id"]
    user = msg.get("from", {})
    tg_id = user.get("id")
    username = (user.get("username") or "").lower()
    if tg_id is None:
        return

    store.ensure_user(tg_id, username)
    remember_admin(store, tg_id, username)
    parts = text.split(maxsplit=1)
    cmd = parts[0].split("@")[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/start", "/help"):
        send(
            chat_id,
            "Quatrogram bot.\n"
            "/number — выдать персональный номер и код\n"
            "/code — показать текущий код\n"
            "/status — статус вашей регистрации\n"
            "Также можно отправить @username или числовой ID для проверки.",
        )
        return

    if cmd == "/number":
        phone, code, registered = store.issue_number(tg_id)
        if registered:
            send(chat_id, f"Вы уже зарегистрированы.\nНомер: {pretty_phone(phone)}")
        else:
            send(
                chat_id,
                f"Ваш номер: {pretty_phone(phone)}\n"
                f"Код: {code}\n"
                "Введите его в клиенте Quatrogram. Код также попадёт в сервер "
                "при нажатии «Отправить код».",
            )
        return

    if cmd == "/code":
        row = store.user(tg_id)
        if not row or not row.get("phone"):
            send(chat_id, "Сначала запросите номер: /number")
        else:
            send(chat_id, f"Номер: {pretty_phone(row['phone'])}\nКод: {row['code'] or '—'}")
        return

    if cmd == "/status":
        send(chat_id, describe(store, store.user(tg_id)))
        return

    if cmd in ("/find", "/check", "/confirm"):
        if not is_admin(tg_id, username):
            send(chat_id, "Команда доступна только администратору.")
            return
        rows = store.find(arg)
        if not rows:
            send(chat_id, "Пользователь не найден.")
            return
        if cmd == "/confirm":
            store.confirm(rows)
            send(chat_id, "Регистрация подтверждена, пользователь уведомлён.")
        else:
            send(chat_id, "\n\n".join(describe(store, r) for r in rows[:10]))
        return

    # Bare @username or numeric ID also performs a lookup (admin only).
    if is_admin(tg_id, username) and (text.startswith("@") or text.isdigit()):
        rows = store.find(text)
        send(chat_id, "\n\n".join(describe(store, r) for r in rows[:10]) if rows else "Не найден.")


def notify_registered(store):
    admins = all_admin_chat_ids(store)
    for row in store.pending_admin_notifications():
        username = f"@{row['username']}" if row.get("username") else "—"
        text = (
            "Новая регистрация в Quatrogram.\n"
            f"ID пользователя: {row['tg_id']}\n"
            f"Юзернейм: {username}\n"
            f"Номер: {pretty_phone(row['phone'])}\n"
            f"ID в Quatrogram: {row.get('user_id') or '—'}"
        )
        for admin in admins:
            send(admin, text)
        store.mark_admin_notified(row["tg_id"])

    for row in store.pending_notifications():
        send(
            row["tg_id"],
            "Регистрация в Quatrogram прошла успешно.\n"
            f"ID пользователя: {row['tg_id']}\n"
            f"Номер: {pretty_phone(row['phone'])}\n"
            f"ID в Quatrogram: {row.get('user_id') or '—'}",
        )
        store.mark_notified(row["tg_id"])


def poll_once(store):
    offset = store.get_state("offset", "0")
    data = api_call(
        "getUpdates",
        params={"offset": offset, "timeout": 10, "allowed_updates": '["message"]'},
    )
    updates = data.get("result", [])
    for upd in updates:
        if "message" in upd:
            handle(store, upd["message"])
        offset = max(int(offset), upd["update_id"] + 1)
    if updates:
        store.set_state("offset", offset)

    # gramsrv writes registered_at after auth.SignUp succeeds.
    notify_registered(store)


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN is not set", file=sys.stderr)
        return 1

    store = Store()
    if os.environ.get("BOT_ONE_SHOT") == "1":
        poll_once(store)
        return 0

    while True:
        try:
            poll_once(store)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            # Do not print exception text: it may contain the bot token URL.
            print(f"poll failed: {type(exc).__name__}; retrying", file=sys.stderr)
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
