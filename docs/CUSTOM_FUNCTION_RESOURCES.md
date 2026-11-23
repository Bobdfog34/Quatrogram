# Источники для кастомных функций Quatrogram

Подборка репозиториев, откуда можно брать готовые решения и патчи.

## Сервер и регистрация (главное для бота)

| Репозиторий | Что даёт |
| --- | --- |
| `iamxvbaba/gramsrv` | Открытый MTProto-сервер на Go, под который уже патчен наш клиент. Здесь живут `sendCode`, `signIn`, генерация и проверка кодов. Основной объект для интеграции с ботом и общим PostgreSQL. |
| `teamgram/teamgram-server` | Альтернативный MTProto-сервер на Go, основа для gramsrv. Полезно сравнить флоу авторизации. |
| `iamxvbaba/proto` | MTProto-библиотеки/схемы, используемые teamgram. |
| `iamxvbaba/td` | Клиент MTProto на Go — удобно для тестов авторизации без Android. |

## Клиенты под тот же сервер (готовые патчи)

| Репозиторий | Что даёт |
| --- | --- |
| `iamxvbaba/gramsrv-telegram` | Исходник Android-клиента, из которого уже взяты коммиты для Quatrogram. |
| `iamxvbaba/gramsrv-tdesktop` | Desktop-клиент под gramsrv. |
| `iamxvbaba/gramsrv-Telegram-iOS` | iOS-клиент под gramsrv. |
| `iamxvbaba/gramsrv-tweb` | Web K под gramsrv. |
| `iamxvbaba/gramsrv-telegram-tt` | Telegram T под gramsrv. |

## Клиентские форки с кастомными функциями

| Репозиторий | Что даёт |
| --- | --- |
| `Nekogram/Nekogram` | Классические моды: приватность, кастомные настройки, улучшения UI. |
| `forkgram/TelegramAndroid` | Большой набор feature-патчей поверх официального Android-исходника. |
| `Telegram-FOSS-Team/Telegram-FOSS` | FOSS-ветка,.clean up Google-зависимостей. |
| `feedelphix/telegram_foss_fork` | Сборка фич из Nekogram(X), Forkgram, Catogram + авторские. |
| `exteraSquad/exteraGram` | Клиент с собственной системой плагинов. |
| `thebadinteger/exteraGram` | Деобфускированный компилируемый исходник exteraGram. |
| `Catogram/Catogram` | Экспериментальный клиент на официальных исходниках. |
| `teidesu/inugram` | Patchset формата queue наверх апстрима — хороший пример организации патчей. |
| `confeden/Novagram` | Приватность: PIN, decoy-режим, self-destruct, DNS-over-HTTPS. |
| `AyuGram/AyuGramDocs` | Документация по функциям AyuGram (ghost mode, история сообщений и т.д.). |
| `exteraSquad/exteraGram` + `0niel/exteraStore` | Пример каталога плагинов: Next.js + PostgreSQL + загрузка/версионирование плагинов. |
| `mr-Vestr/plugins` | Готовые плагины: шаблоны сообщений, plugin creator, ADB Lite. |

## Плагины/хуки без пересборки клиента

| Репозиторий | Что даёт |
| --- | --- |
| `cinit/TMoe` | Xposed-модуль с большим набором функций для Telegram-клиентов. |
| `Nep-Timeline/Re-Telegram` | Xposed-модуль улучшений Telegram. |
| `std-microblock/TGStickerProvider` | Пример LSPosed-плагина, работает со многими клиентами. |

## Ботовая инфраструктура

| Репозиторий | Что даёт |
| --- | --- |
| `yagop/telegram-bot` | Классический plugin-based Telegram-бот на Python. |
| `datamachine/telex` | Plugin-based Python Telegram Bot. |
| `Bibo-Joshi/ptbstats` | Пример статистического плагина для python-telegram-bot. |
| `python-telegram-bot/python-telegram-bot` | Основная библиотека для бота. |

## TDLib

| Репозиторий | Что даёт |
| --- | --- |
| `tdlib/td` | Эталон MTProto-клиентской логики, полезно для сверки схем и авторизации. |

## Приоритет

1. `gramsrv` — разобрать флоу кодов и регистрации, подключить нашего бота и PostgreSQL.
2. `exteraGram` / `mr-Vestr/plugins` — понять модель плагинов и взять идеи для кастомных функций.
3. `Nekogram` / `Forkgram` — точечные UI/privacy-патчи, которые не ломают сборку.
4. Xposed-модули — только если нужно без пересборки APK.
