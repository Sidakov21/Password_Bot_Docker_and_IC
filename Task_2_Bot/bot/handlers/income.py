from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot import db
from bot.keyboards import MENU_BUTTONS, cancel_kb, main_menu, skip_kb

router = Router()


class Income(StatesGroup):
    amount = State()
    comment = State()


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
    cleaned = message.text.strip().replace(" ", "").replace("\u00a0", "")
    if not cleaned.isdigit() or int(cleaned) <= 0:
        await message.answer("Сумма — положительное целое число. Пример: 50000")
        return
    await state.update_data(amount=int(cleaned))
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

    data = await state.get_data()
    await db.add_operation(message.from_user.id, "income", data["amount"], None, comment)
    await state.clear()
    text = f"✅ Доход записан: +{data['amount']} ₽"
    if comment:
        text += f" ({comment})"
    await message.answer(text, reply_markup=main_menu())
