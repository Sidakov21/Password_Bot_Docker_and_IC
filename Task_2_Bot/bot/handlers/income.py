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
    skip_kb,
    undo_inline,
)

router = Router()


class Income(StatesGroup):
    amount = State()
    comment = State()
    category = State()


@router.message(F.text == "Доход")
async def ask_income(message: Message, state: FSMContext) -> None:
    await state.set_state(Income.amount)
    await message.answer(
        "Введите сумму дохода (целое число):",
        reply_markup=cancel_kb,
    )


@router.message(Income.amount)
async def income_amount(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Отправьте число, например: 50000")
        return
    if message.text in MENU_BUTTONS:
        await state.clear()
        await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())
        return
    cleaned = message.text.strip()
    import re

    m = re.findall(r"-?\d+", cleaned)
    if not m:
        await message.answer("Не понял сумму. Пример: 50000")
        return
    amount = int(m[0])
    if amount <= 0:
        await message.answer("Сумма — положительное целое число. Пример: 50000")
        return
    await state.update_data(amount=amount)
    await state.set_state(Income.comment)
    await message.answer(
        "Добавьте комментарий или нажмите «Пропустить»:",
        reply_markup=skip_kb,
    )


@router.message(Income.comment)
async def income_comment(message: Message, state: FSMContext) -> None:
    if message.text is None or message.text in MENU_BUTTONS:
        await state.clear()
        await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())
        return
    comment = None
    if message.text.strip() != "Пропустить":
        comment = message.text.strip()

    await state.update_data(comment=comment)
    await state.set_state(Income.category)
    categories = await db.get_categories(message.from_user.id) or ["Другое"]
    await message.answer("Выберите категорию дохода:", reply_markup=categories_inline(categories))


@router.callback_query(Income.category, F.data.startswith("cat:"))
async def income_category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = callback.data.split(":", 1)[1]
    op_id = await db.add_operation(
        callback.from_user.id,
        "income",
        data["amount"],
        category,
        data.get("comment"),
    )
    await state.clear()
    text = f"✅ Доход записан: +{data['amount']} ₽ ({category})"
    if data.get("comment"):
        text = f"✅ Доход записан: +{data['amount']} ₽ ({data['comment']}, {category})"
    if callback.message:
        await callback.message.edit_text(text, reply_markup=undo_inline(op_id))
    await callback.answer("Сохранено")
    if callback.message:
        await callback.message.answer(
            "Выберите действие в меню 👇", reply_markup=main_menu()
        )
