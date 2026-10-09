import asyncio
from datetime import datetime
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from bot import db
from bot.keyboards import main_menu

router = Router()

MONTHS = (
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
)


def build_chart(title: str, by_category: list[tuple]) -> bytes:
    labels = [row[0] for row in by_category]
    values = [row[1] for row in by_category]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        values,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        pctdistance=0.75,
        textprops={"fontsize": 10},
    )
    ax.axis("equal")
    ax.set_title(title)

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    return buf.getvalue()


@router.message(F.text == "Отчёт")
async def show_report(message: Message, state: FSMContext) -> None:
    await state.clear()
    now = datetime.now()
    stats = await db.get_month_stats(message.from_user.id, now.year, now.month)

    expense = stats["expense"]
    income = stats["income"]
    balance = income - expense
    month_title = f"за {MONTHS[now.month - 1]} {now.year}"

    if income == 0 and expense == 0:
        await message.answer(
            f"📊 Отчёт {month_title} пуст.\n"
            "Нет ни доходов, ни расходов. Добавьте первую операцию.",
            reply_markup=main_menu(),
        )
        return

    lines = [
        f"📊 Отчёт {month_title}",
        "",
        f"💰 Доходы: {income} ₽",
        f"💸 Расходы: {expense} ₽",
        f"⚖️ Баланс: {balance} ₽",
    ]

    by_category = stats["by_category"]
    if by_category:
        lines.append("")
        lines.append("Расходы по категориям:")
        for category, total in by_category:
            lines.append(f"  • {category}: {total} ₽")

    await message.answer("\n".join(lines), reply_markup=main_menu())

    if expense > 0 and by_category:
        title = f"Расходы {month_title}"
        png = await asyncio.to_thread(build_chart, title, by_category)
        await message.answer_photo(
            BufferedInputFile(png, filename="report.png"),
            caption="Распределение расходов по категориям",
        )
