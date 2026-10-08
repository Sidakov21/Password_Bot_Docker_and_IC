from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu

router = Router()

STUB_SECTIONS = {"Отчёт": "этап 4", "История": "этап 5", "Категории": "этап 3"}


@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменено. Выберите действие:", reply_markup=main_menu())


@router.message(F.text.in_(STUB_SECTIONS))
async def stub(message: Message, state: FSMContext) -> None:
    await state.clear()
    stage = STUB_SECTIONS.get(message.text, "")
    await message.answer(
        f"⏳ Раздел «{message.text}» в разработке, будет на {stage} плана."
    )


@router.callback_query(F.data == "fsm_cancel")
async def inline_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Отменено")
    if callback.message:
        await callback.message.edit_text("❌ Отменено")
