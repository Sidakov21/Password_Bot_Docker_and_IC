from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

MENU_BUTTONS = ("Расход", "Доход", "Отчёт", "История", "Категории", "Помощь")


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in MENU_BUTTONS],
        resize_keyboard=True,
    )


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отмена")]],
    resize_keyboard=True,
)

skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]],
    resize_keyboard=True,
)


def categories_inline(categories: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"cat:{name}")]
        for name in categories
    ]
    rows.append(
        [InlineKeyboardButton(text="❌ Отмена", callback_data="fsm_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def undo_inline(op_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Отменить запись", callback_data=f"undo:{op_id}"
                )
            ]
        ]
    )
