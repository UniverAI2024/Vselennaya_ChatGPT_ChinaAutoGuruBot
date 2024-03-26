from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = [
        [types.KeyboardButton(text="Начать консультацию")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)
    return keyboard


def close_menu_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = [
        [types.KeyboardButton(text="Оценить консультацию")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)
    return keyboard


def drating_inline_buttons_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=str(i), callback_data=f"drate_{i}") for i in range(1, 6)],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

