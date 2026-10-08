from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import db
from bot.keyboards import main_menu

router = Router()

HELP = (
    "Я — «Копилка», бот для учёта бюджета.\n\n"
    "💸 Расход — записать трату (описание + сумма)\n"
    "💰 Доход — записать поступление\n"
    "📊 Отчёт — итоги за месяц\n"
    "🕘 История — последние операции\n"
    "📁 Категории — создать / переименовать / удалить\n\n"
    "Команды: /start — меню, /help — эта справка"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db.ensure_default_categories(message.from_user.id)
    await message.answer(
        "Привет! Я «Копилка» — бот для учёта доходов и расходов.\n"
        "Выберите действие в меню 👇",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(HELP, reply_markup=main_menu())
