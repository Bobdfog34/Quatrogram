# Quatrogram

MTProto-клиент для self-hosted сервера gramsrv.

- **Версия в приложении:** `13.3.1` (код `7310`)
- **База исходников:** официальный Android-клиент `13.2.2`, патчи gramsrv и локальные правки Quatrogram
- **Сервер:** вшит в APK, переключение датацентров отключено
- **Публичный домен ссылок:** `quatrogram.net`
- **APK:** [Quatrogram-13.3.1.apk](https://github.com/Bobdfog34/Quatrogram/releases/download/v13.3.1/Quatrogram-13.3.1.apk)

## Что включено

- брендинг Quatrogram без упоминаний стороннего бренда в интерфейсе;
- заголовок приложения по центру;
- кошельки, балансы Gram и Stars включены для всех пользователей;
- код подключения и RSA-ключ сервера зашиты в сборку;
- бот регистрации с уникальными номерами и кодами.

## Бот регистрации

Бот выдаёт пользователю персональный номер и 5-значный код, проверяет регистрацию по ID и юзернейму и отправляет администратору отчёт с ID пользователя и номером.

Команды: `/number`, `/code`, `/status`, `/find @username`, `/confirm @username`.

Администратор: `@VUral_Gaisin`.

Для GitHub Actions нужны секреты:

- `BOT_TOKEN` — токен бота;
- `ADMIN_USERNAMES` — `VUral_Gaisin`;
- `ADMIN_CHAT_IDS` — числовой чат администратора, если известен;
- `DATABASE_URL` — PostgreSQL, если используется общая БД с сервером.

Без `DATABASE_URL` бот использует SQLite и кэширует состояние в GitHub Actions.

## Сборка

Основной экшен: `.github/workflows/build.yml`.

```bash
./gradlew :TMessagesProj_App:assembleAfatRelease --stacktrace --no-daemon
```

Импорт и наложение правок: `.github/workflows/import.yml` и `.github/scripts/finalize.py`.

## Интеграция с сервером

Патч gramsrv описан в [docs/GRAMSVR_REGISTRATION_PATCH.md](docs/GRAMSVR_REGISTRATION_PATCH.md). Redis остаётся авторитетным хранилищем кодов; выданный ботом код подставляется только на выдаче, а успешная регистрация отмечается в отдельной таблице.

## Плагины

Дизайн безопасной системы плагинов описан в [docs/QUATROGRAM_PLUGIN_SYSTEM.md](docs/QUATROGRAM_PLUGIN_SYSTEM.md). Используются декларативные `.qplugin`-манифесты без выполнения произвольного кода.

## Лицензия

Основано на исходном коде MTProto-клиента и патчах gramsrv под GPL-2.0-or-later. Проект не аффилирован со сторонними сервисами.
