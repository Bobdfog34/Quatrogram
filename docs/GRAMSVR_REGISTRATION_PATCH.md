# Интеграция регистрации Quatrogram с gramsrv

Источник: `https://github.com/iamxvbaba/gramsrv` (ветка `main`).

Ключевой вывод: **не надо** заменять Redis `CodeStore` и не надо писать код через OTP-webhook.
gramsrv уже владеет генерацией, TTL, попытками и проверкой кода в Redis. Нужно только:

1. подставить код бота в `store.PhoneCode.Code` в момент `auth.sendCode` / `auth.resendCode`;
2. после успешного `auth.SignUp` отметить registration в отдельной таблице PostgreSQL.

## 1. Миграция PostgreSQL

Новые файлы:

- `deploy/migrations/20261123000000_bot_registration_codes.up.sql`
- `deploy/migrations/20261123000000_bot_registration_codes.down.sql`

```sql
CREATE TABLE public.telegram_bot_registration_codes (
    phone            varchar(32) PRIMARY KEY,
    code             varchar(10) NOT NULL,
    issued_at        timestamptz NOT NULL DEFAULT now(),
    expires_at       timestamptz NOT NULL,
    claimed_at       timestamptz,
    registered_at    timestamptz,
    telegram_user_id bigint,
    user_id          bigint,
    updated_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX telegram_bot_registration_codes_pending_idx
    ON public.telegram_bot_registration_codes (issued_at DESC)
    WHERE claimed_at IS NULL AND registered_at IS NULL;
```

`down.sql`: `DROP TABLE public.telegram_bot_registration_codes;`

Не добавляем `registered_at` в `users` — это bot-owned состояние.

## 2. Маленький PG-store

Новый файл `internal/store/postgres/telegram_bot_code.go`:

```go
type TelegramBotCodeStore struct { pool *pgxpool.Pool }

func (s *TelegramBotCodeStore) ClaimActive(ctx context.Context, phone string) (string, time.Time, error) {
    var code string
    var expiresAt time.Time
    err := s.pool.QueryRow(ctx, `
        UPDATE public.telegram_bot_registration_codes
           SET claimed_at = now(), updated_at = now()
         WHERE phone = $1
           AND registered_at IS NULL
           AND expires_at > now()
        RETURNING code, expires_at`, phone).Scan(&code, &expiresAt)
    return code, expiresAt, err
}

func (s *TelegramBotCodeStore) MarkRegistered(ctx context.Context, phone string, userID int64) error {
    _, err := s.pool.Exec(ctx, `
        UPDATE public.telegram_bot_registration_codes
           SET registered_at = now(), user_id = $2, updated_at = now()
         WHERE phone = $1 AND registered_at IS NULL`, phone, userID)
    return err
}
```

`ClaimActive` — идемпотентный: повторный `sendCode` / `resendCode` получает тот же
активный код. Это важно, иначе `resendCode` сломается после первого `sendCode`.
Бот перезаписывает строку только когда выдаёт пользователю новый номер/код.
Если сервер умеет задавать TTL явно, используйте вернувшийся `expiresAt`, иначе
оставляйте текущий TTL gramsrv.

## 3. Опции в `auth.Service`

Файл `internal/app/auth/service.go`.

```go
externalPhoneCode   func(ctx context.Context, phone string) (string, time.Time, error)
registrationObserver func(ctx context.Context, phone string, userID int64) error

func WithExternalPhoneCodeSource(src func(context.Context, string) (string, time.Time, error)) Option { ... }
func WithRegistrationObserver(obs func(context.Context, string, int64) error) Option { ... }
```

В `createPhoneCode` после получения `hash`:

```go
if s.externalPhoneCode != nil && existingUserID == 0 {
    code, _, err = s.externalPhoneCode(ctx, phone)
    if err == nil {
        channel = codeChannelSMS
    }
}
```

`resendCode` уже вызывает `createPhoneCode`, отдельно патчить не надо.

В `SignUp` сразу после `s.bind(ctx, auth, u.ID)`:

```go
if s.registrationObserver != nil {
    if err := s.registrationObserver(ctx, phone, u.ID); err != nil {
        // registration already committed — only log/metric
    }
}
```

Важно: `s.codes.Set(...)` оставляем как есть. Redis остаётся авторитетным верификатором.

## 4. Проводка в `cmd/telesrv/main.go`

Рядом с `codeStore := redisstore.NewCodeStore(rdb)` создаём `botCodeStore := postgres.NewTelegramBotCodeStore(pool)`.

В вызов `auth.NewService(...)` добавляем:

```go
auth.WithExternalPhoneCodeSource(botCodeStore.ClaimActive),
auth.WithRegistrationObserver(botCodeStore.MarkRegistered),
```

## 5. Нормализация телефона

`domain.NormalizePhone()` возвращает только цифры без `+`. Бот делает то же самое:
`re.sub(r"\D", "", value)`. Лимит: 4..32 цифры (runtime), не 5, как в комментарии auth-сервиса.

## 6. Тесты

- `internal/app/auth/service_test.go`: external code source используется в `SendCode`; `SignIn` принимает код бота; `SignUp` вызывает observer.
- Новый PG integration test: `ClaimActive` идемпотентен, учитывает `expires_at` и не работает после `registered_at`; `MarkRegistered` идемпотентен.
- Существующие `code_cas_integration_test.go` и `login_code_integration_test.go` должны остаться зелёными.

## Отвергнутый вариант

Делать `store.CodeStore` на PostgreSQL — слишком рискованно: интерфейс включает
`VerifyLogin`, `ConsumeSignUpVerified`, `TakeLoginCode`, CAS/revision и TTL-логику на Lua.
Лучше оставить Redis и только подставлять код на issuance.
