from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import db
from bot.keyboards import history_inline, main_menu

router = Router()

ICON = {"expense": "💸", "income": "💰"}


def format_operation(row) -> str:
    op_id, op_type, amount, category, comment, created_at = row
    icon = ICON.get(op_type, "•")
    sign = "-" if op_type == "expense" else "+"
    line = f"{icon} #{op_id} {sign}{amount} ₽"
    if category:
        line += f" [{category}]"
    if comment:
        line += f" — {comment}"
    line += f" · {created_at[:16].replace('T', ' ')}"
    return line


@router.message(F.text == "История")
async def show_history(message: Message, state: FSMContext) -> None:
    await state.clear()
    rows = await db.get_history(message.from_user.id, limit=10)
    if not rows:
        await message.answer(
            "История пуста. Добавьте первую операцию.", reply_markup=main_menu()
        )
        return
    lines = ["🕘 Последние операции:", ""]
    lines.extend(format_operation(row) for row in rows)
    op_ids = [row[0] for row in rows]
    await message.answer(
        "\n".join(lines),
        reply_markup=history_inline(op_ids),
    )


@router.callback_query(F.data.startswith("delop:"))
async def delete_history_item(callback: CallbackQuery) -> None:
    op_id = int(callback.data.split(":", 1)[1])
    removed = await db.delete_operation(callback.from_user.id, op_id)
    await callback.answer("Удалено" if removed else "Уже удалено")
    if not callback.message:
        return
    if removed:
        await callback.message.answer(
            f"🗑 Операция #{op_id} удалена.", reply_markup=main_menu()
        )
    else:
        await callback.message.answer(
            f"Операция #{op_id} уже была удалена.", reply_markup=main_menu()
        )
