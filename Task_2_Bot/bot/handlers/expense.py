from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot import db
from bot.keyboards import (
    MENU_BUTTONS,
    cancel_kb,
    categories_inline,
    main_menu,
    undo_inline,
)

router = Router()


class Expense(StatesGroup):
    input = State()
    category = State()


def parse_expense(text: str) -> tuple[int, str | None] | None:
    parts = text.rstrip()
    import re

    m = re.findall(r"(-?\d+)", parts)
    if not m:
        return None
    amount = int(m[-1])
    if amount <= 0:
        return None
    comment = re.sub(r"\s*" + re.escape(str(amount)) + r"\s*$", "", parts).strip()
    comment = re.sub(r"^\s*" + re.escape(str(amount)) + r"\s*", "", comment).strip()
    if not comment:
        return amount, None
    return amount, comment


@router.message(F.text == "Расход")
async def ask_expense(message: Message, state: FSMContext) -> None:
    await state.set_state(Expense.input)
    await message.answer(
        "Введите описание и сумму одной строкой.\nНапример: кофе 250",
        reply_markup=cancel_kb,
    )


@router.message(Expense.input)
async def expense_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Отправьте текстом, например: кофе 250")
        return
    if message.text in MENU_BUTTONS:
        await state.clear()
        await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())
        return
    parsed = parse_expense(message.text)
    if parsed is None:
        await message.answer("Не понял сумму. Пример: кофе 250 (целое число рублей)")
        return
    amount, comment = parsed
    await state.update_data(amount=amount, comment=comment)
    await state.set_state(Expense.category)
    categories = await db.get_categories(message.from_user.id) or ["Другое"]
    await message.answer(
        "Выберите категорию:", reply_markup=categories_inline(categories)
    )


@router.callback_query(Expense.category, F.data.startswith("cat:"))
async def category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = callback.data.split(":", 1)[1]
    op_id = await db.add_operation(
        callback.from_user.id,
        "expense",
        data["amount"],
        category,
        data.get("comment"),
    )
    await state.clear()
    comment = data.get("comment")
    title = f"{comment} — " if comment else ""
    if callback.message:
        await callback.message.edit_text(
            f"✅ Расход записан: {title}{data['amount']} ₽ ({category})",
            reply_markup=undo_inline(op_id),
        )
    await callback.answer("Сохранено")
    await callback.message.answer("Выберите действие в меню 👇", reply_markup=main_menu())


@router.callback_query(F.data.startswith("undo:"))
async def undo_operation(callback: CallbackQuery) -> None:
    op_id = int(callback.data.split(":", 1)[1])
    removed = await db.delete_operation(callback.from_user.id, op_id)
    await callback.answer("Удалено" if removed else "Уже удалено")
    if callback.message:
        await callback.message.edit_text(
            "🗑 Запись удалена" if removed else "Запись уже была удалена"
        )
    await callback.message.answer("Выберите действие в меню 👇", reply_markup=main_menu())

