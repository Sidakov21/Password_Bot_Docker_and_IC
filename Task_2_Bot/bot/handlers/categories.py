from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from bot import db
from bot.keyboards import MENU_BUTTONS, cancel_kb, main_menu

router = Router()


class Categories(StatesGroup):
    action = State()
    new_name = State()
    rename_old = State()
    rename_new = State()
    delete = State()


async def _leave_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())


@router.message(F.text == "Категории")
async def cats(message: Message, state: FSMContext):
    await db.ensure_default_categories(message.from_user.id)
    await state.set_state(Categories.action)
    cats_list = ", ".join(await db.get_categories(message.from_user.id))
    await message.answer(
        f"Текущие категории: {cats_list}\n\nДействие: создать / переименовать / удалить",
        reply_markup=cancel_kb,
    )


@router.message(Categories.action)
async def cats_action(message: Message, state: FSMContext):
    if message.text is None:
        return
    if message.text in MENU_BUTTONS:
        await _leave_menu(message, state)
        return
    t = message.text.lower()
    if "создат" in t:
        await state.set_state(Categories.new_name)
        await message.answer("Введите название новой категории:", reply_markup=cancel_kb)
        return
    if "переимен" in t:
        await state.set_state(Categories.rename_old)
        cats = await db.get_categories(message.from_user.id)
        await message.answer(
            "Какую категорию переименовать?\n" + ", ".join(cats),
            reply_markup=cancel_kb,
        )
        return
    if "удал" in t:
        await state.set_state(Categories.delete)
        cats = await db.get_categories(message.from_user.id)
        await message.answer(
            "Какую категорию удалить?\n" + ", ".join(cats),
            reply_markup=cancel_kb,
        )
        return
    await message.answer(
        "Не понял. Напиши: создать / переименовать / удалить",
        reply_markup=cancel_kb,
    )


@router.message(Categories.new_name)
async def cats_new(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text in MENU_BUTTONS:
        await _leave_menu(message, state)
        return
    name = message.text.strip()
    ok = await db.add_category(message.from_user.id, name)
    await state.clear()
    if ok:
        await message.answer(f"Категория «{name}» создана.", reply_markup=main_menu())
    else:
        await message.answer("Такая категория уже есть.", reply_markup=main_menu())


@router.message(Categories.rename_old)
async def cats_ren_old(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text in MENU_BUTTONS:
        await _leave_menu(message, state)
        return
    old = message.text.strip()
    await state.update_data(old=old)
    await state.set_state(Categories.rename_new)
    await message.answer("Введите новое название:", reply_markup=cancel_kb)


@router.message(Categories.rename_new)
async def cats_ren_new(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text in MENU_BUTTONS:
        await _leave_menu(message, state)
        return
    new = message.text.strip()
    d = await state.get_data()
    old = d.get("old")
    ok = await db.rename_category(message.from_user.id, old, new)
    await state.clear()
    if ok:
        await message.answer(f"Переименовано: {old} → {new}", reply_markup=main_menu())
    else:
        await message.answer(
            f"Не удалось переименовать: «{new}» уже существует.",
            reply_markup=main_menu(),
        )


@router.message(Categories.delete)
async def cats_del(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text in MENU_BUTTONS:
        await _leave_menu(message, state)
        return
    name = message.text.strip()
    ok = await db.delete_category(message.from_user.id, name)
    await state.clear()
    if ok:
        await message.answer(f"Категория «{name}» удалена.", reply_markup=main_menu())
    else:
        await message.answer("Категория не найдена.", reply_markup=main_menu())
