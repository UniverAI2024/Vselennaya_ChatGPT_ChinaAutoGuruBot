import json
import logging
from aiogram import Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
import asyncio
from datetime import datetime, timezone, timedelta
import os
from create_bot import bot
from core.utils import get_report
from dbase.dbworker import get_user_entry, add_user, update_dialog_state
from keyboards.admin_keyboard import export_inline_buttons_keyboard
from keyboards.user_keyboard import main_menu_keyboard, close_menu_keyboard

timezone_offset = 3.0  # Pacific Standard Time (UTC+03:00)
tzinfo = timezone(timedelta(hours=timezone_offset))

logger = logging.getLogger(__name__)

router = Router()  # [1]
router.message.filter(F.chat.type.in_({"private"}))

welcome_msg = f"<b>Добро пожаловать!</b>\n\nЗадайте вопрос — я готов искать на него ответ."


# Получаем ID текущего модератора:
@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    if not get_user_entry(message.from_user.id):
        user_data = (
            message.from_user.id,
            None,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"),
            None,
            "start",
            0,
            None,
            None,
            0,
            0,
            0,
            None,
            1
        )
        add_user(user_data)
        await message.answer(f"{welcome_msg}",
                             reply_markup=close_menu_keyboard(), parse_mode='HTML')
        # await message.answer(f"{welcome_msg} Если у вас есть вопросы, нажмите <b>'Начать консультацию'</b>",
        #                      reply_markup=main_menu_keyboard(), parse_mode='HTML')
    else:
        await message.answer(f"{welcome_msg}",
                             reply_markup=close_menu_keyboard(), parse_mode='HTML')
        # await bot.send_message(message.from_user.id, f"{welcome_msg} Если у вас есть вопросы, нажмите "
        #                                              "<b>'Начать консультацию'</b>",
        #                        reply_markup=main_menu_keyboard(), parse_mode='HTML')
    update_dialog_state(message.from_user.id, 'start')
    await asyncio.sleep(1)


@router.message(Command(commands=["exportData"]))
async def cmd_export(message: types.Message):
    await message.answer("Нажмите для экспорта данных: ", reply_markup=export_inline_buttons_keyboard())


@router.callback_query(lambda callback_query: callback_query.data == "export")
async def callback_export(callback_query: types.CallbackQuery):
    report_name = get_report()
    await bot.answer_callback_query(callback_query.id)
    doc = types.input_file.FSInputFile(path=report_name, filename=report_name)
    await callback_query.message.answer_document(doc)
    try:
        os.remove(report_name)
    except:
        pass
    await asyncio.sleep(1)

