# Budget-бот «Копилка»

Telegram-бот для учёта доходов и расходов с категориями, отчётом за месяц (с диаграммой) и историей операций.

## Структура
- ot/config.py — конфиг (.env)
- ot/db.py — SQLite
- ot/keyboards.py — меню/кнопки
- ot/handlers/ — хендлеры
- ot/main.py — запуск

## Локальный запуск
1. cd Task_2_Bot
2. Создать .env по образцу .env.example: BOT_TOKEN=...
3. python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
4. .venv\Scripts\python -m bot.main

## Функции
- Расход/Доход с выбором категории
- Категории: создать/переименовать/удалить
- Отчёт за текущий месяц: суммы + баланс + диаграмма расходов
- История последних операций + удаление
