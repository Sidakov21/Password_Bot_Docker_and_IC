import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot import db
from bot.config import BOT_TOKEN
from bot.handlers import common, expense, income, start

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN не найден."
        )

    await db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(start.router)
    dp.include_router(expense.router)
    dp.include_router(income.router)

    print("Бот запущен. Остановка — Ctrl+C")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())