# Тестовое задание — пароль, бот «Копилка», Docker

**Репозиторий:** https://github.com/Sidakov21/Password_Bot_Docker_and_IC

Публичный GitHub-репозиторий с тремя частями домашнего задания: консольный генератор пароля, Telegram-бот учёта бюджета и контейнеризация бота.

## Структура проекта

| Каталог | Содержание |
|---------|------------|
| `Task_1_Password/` | Генератор случайного пароля (Python) |
| `Task_2_Bot/` | Telegram-бот «Копилка» (aiogram 3, SQLite, matplotlib) |
| `Task_3_Docker/` | `Dockerfile` и `docker-compose.yml` для бота |
| `Task_2_Bot/ПЛАН.md` | Пошаговый план разработки бота (как подходил к задаче) |

---

## Как запустить проекты

### Task 1 — генератор пароля

**Требования:** Python 3.10+

```powershell
cd Task_1_Password
python script.py
```

Введите длину пароля (целое число больше 0). Пароль собирается из латинских букв (`a–z`, `A–Z`) и цифр.

### Task 2 — бот «Копилка» (локально)

**Требования:** Python 3.11+, токен от [@BotFather](https://t.me/BotFather)

```powershell
cd Task_2_Bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

В `Task_2_Bot/.env`:

```env
BOT_TOKEN=ваш_токен_от_BotFather
```

Запуск:

```powershell
python -m bot.main
```

В консоли должно появиться сообщение «Бот запущен. Остановка — Ctrl+C». В Telegram: `/start`, затем кнопки меню (Расход, Доход, Отчёт, История, Категории, Помощь).

База данных создаётся автоматически: `Task_2_Bot/data/budget.db`.

**Проверено локально:** компиляция модулей (`python -m compileall bot`), инициализация БД, импорт всех хендлеров.

---

## Как запустить бота через Docker

**Требования:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (или Docker Engine + Compose).

1. Создайте `Task_2_Bot/.env` с `BOT_TOKEN` (см. выше). Файл `.env` в git не попадает.
2. Из корня репозитория:

```powershell
cd Task_3_Docker
docker compose up --build -d
```

Просмотр логов:

```powershell
docker compose logs -f kopilka-bot
```

Остановка:

```powershell
docker compose down
```

Данные SQLite хранятся в томе Docker `kopilka_data` (не теряются при перезапуске контейнера).

**Проверено:** `docker compose build` успешно собирает образ `task_3_docker-kopilka-bot`.

---

## Функции бота

- Запись **расходов** (текст + сумма, категория) и **доходов**
- **Отчёт** за текущий месяц: доходы, расходы, баланс, список по категориям, круговая диаграмма (PNG)
- **История** последних 10 операций с удалением
- **CRUD категорий** (создать / переименовать / удалить; при переименовании обновляются и старые операции)
- Отмена FSM и кнопка «Отменить запись» после сохранения

---

## Источники и материалы

При выполнении работы использовались открытые материалы:

| Тема | Источник |
|------|----------|
| Telegram Bot API, создание бота | [Документация Telegram Bots](https://core.telegram.org/bots), [@BotFather](https://t.me/BotFather) |
| Фреймворк бота | [Документация aiogram 3](https://docs.aiogram.dev/) |
| Асинхронный SQLite | [Документация aiosqlite](https://aiosqlite.omnilib.dev/) |
| Диаграммы в отчёте | [Matplotlib](https://matplotlib.org/stable/users/index.html) |
| Переменные окружения | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Docker | [Docker Docs — Dockerfile](https://docs.docker.org/reference/dockerfile/), [Compose](https://docs.docker.com/compose/) |
| Python: `random`, строки | [Документация Python — random](https://docs.python.org/3/library/random.html), [string](https://docs.python.org/3/library/string.html) |

Дополнительно — официальные README библиотек на PyPI, примеры FSM и inline-клавиатур в документации aiogram.

---

## Использование ИИ

По условиям задания указано, какие инструменты использовались:

| Инструмент | Для чего |
|------------|----------|
| **OpenCode**, модель **Big Pickle** | Черновая структура проекта, набросок логики, первичные идеи по боту и Docker |
| **Cursor**, модель **Composer 2.5 Fast** | Дополнение и правка кода, исправление ошибок, smoke-тесты, заполнение README и Docker-файлов, проверка сборки |

Самостоятельно: постановка задачи, план в `ПЛАН.md`, настройка окружения, токен бота, ручная проверка сценариев в Telegram, коммиты в Git.

---

## Лицензия

Учебный проект (информационный комитет / тестовое задание).
