import json
import logging
import asyncio
import pickle
from langchain.memory import ConversationBufferMemory
from datetime import datetime, timezone, timedelta
from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.utils import split_messages
from create_bot import bot
from core import main_chatgpt
from dbase.dbworker import update_last_dialog, get_user, \
    update_dialog_state, update_dialog_score, add_history, update_qa, update_last_num_token, update_last_time_duration, \
    update_num_queries, update_buffer_memory, update_last_interaction
from keyboards.user_keyboard import main_menu_keyboard, drating_inline_buttons_keyboard, close_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()  # [2]
router.message.filter(F.chat.type.in_({"private"}))


timezone_offset = 3.0  # Pacific Standard Time (UTC+03:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


@router.message(lambda message: message.text == "Оценить консультацию")
async def process_close_consultation(message: types.Message, state: FSMContext):
    if get_user(message.from_user.id)[7] == 'open':
        await message.reply("Консультация завершена. Если у вас возникнут еще вопросы, не стесняйтесь задавать их "
                            "после оценки качества")
        await message.answer("Пожалуйста, оцените качество консультации от 1 до 5:",
                             reply_markup=drating_inline_buttons_keyboard())
        update_dialog_state(message.from_user.id, 'close')
    elif get_user(message.from_user.id)[7] == 'close':
        await message.answer("Пожалуйста, оцените качество консультации от 1 до 5:",
                             reply_markup=drating_inline_buttons_keyboard())
    else:
        await message.reply("Вы еще не задавали новые вопросы сегодня.\n\n"
                            "Пожалуйста, напишите ваш вопрос, и после ответа сможете "
                            "оценить качество полученной консультации",
                            reply_markup=close_menu_keyboard())
        update_dialog_state(message.from_user.id, 'start')
    await asyncio.sleep(1)


@router.callback_query(lambda c: c.data.startswith("drate_"))
async def process_callback_drating(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = get_user(callback_query.from_user.id)
    if user_data[7] == 'close':
        rating = int(callback_query.data[6:])
        await bot.answer_callback_query(callback_query.id, text=f"Спасибо за вашу оценку: {rating}!", show_alert=True)
        await bot.send_message(callback_query.from_user.id, f"Спасибо за вашу оценку: {rating}!",
                               reply_markup=close_menu_keyboard())
        update_dialog_state(callback_query.from_user.id, 'finish')
        # Здесь сохраняется оценка пользователя для дальнейшего анализа или использования
        update_dialog_score(callback_query.from_user.id, rating)
        # Запись истории
        history_data = (
            callback_query.from_user.id,
            "Консультация ТГ-бот",
            user_data[10],
            rating,
            user_data[11],
            datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"),
            user_data[12],
            user_data[15]

        )
        add_history(history_data)

        await state.clear()
    await bot.answer_callback_query(callback_query.id)
    await asyncio.sleep(1)


@router.message(lambda message: get_user(message.from_user.id)[7] in ['start', 'finish'])
async def generate_answer(message: types.Message, state: FSMContext):
    update_last_num_token(message.from_user.id, 0)
    update_last_time_duration(message.from_user.id, 0)
    user_data = get_user(message.from_user.id)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    msg = await message.answer("Я ищу для Вас информацию. Ожидайте...⏳")
    topic = message.text
    logger.info(topic)
    try:
        time1 = datetime.now(tzinfo)
        completion, dialog, total_tokens = await main_chatgpt.get_chatgpt_ansver(topic, memory, k=6)
        time2 = datetime.now(tzinfo)
        duration = time2 - time1
        await msg.edit_text(completion)
        # await state.update_data(messages_dialog_id=json.dumps([message.message_id, msg.message_id]))
        update_last_dialog(message.from_user.id, json.dumps(dialog))
        update_dialog_state(message.from_user.id, 'open')
        update_qa(message.from_user.id, (topic,
                                         f"Пользователь: {topic}\nАссистент: {completion}\n\n"))
        update_last_num_token(message.from_user.id, int(total_tokens))
        update_last_time_duration(message.from_user.id, int(duration.total_seconds()))
        update_num_queries(message.from_user.id, user_data[13]+1)
        update_buffer_memory(message.from_user.id, pickle.dumps(memory))
        update_last_interaction(message.from_user.id, datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as error:
        await bot.send_message(message.from_user.id, f"ОШИБКА: {error}")
        logger.error(f"ОШИБКА generate_answer: {error}")

    await asyncio.sleep(1)


@router.message(lambda message: get_user(message.from_user.id)[7] == 'open')
async def generate_second_answer(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    # last_messages_id = json.loads(state_data["messages_dialog_id"])
    # last_messages_id.append(message.message_id)
    user_data = get_user(message.from_user.id)
    topic = message.text
    last_dialog = json.loads(user_data[6])

    memory = pickle.loads(user_data[14])
    msg = await message.answer("Я ищу для Вас информацию. Ожидайте...⏳")
    try:
        time1 = datetime.now(tzinfo)
        completion, dialog, total_tokens = await main_chatgpt.get_chatgpt_second_answer(last_dialog, topic,
                                                                    user_data[9], memory, k=4)
        time2 = datetime.now(tzinfo)
        duration = time2 - time1
        await msg.edit_text(completion)
        # last_messages_id.append(msg.message_id)
        new_qa = "\n".join(
            [user_data[10], f"Пользователь: {topic}\nАссистент: {completion}\n\n"])
        update_last_dialog(message.from_user.id, json.dumps(dialog))
        logger.info(f"Сообщение: ({dialog}) ")
        update_qa(message.from_user.id, (topic, new_qa))
        update_last_num_token(message.from_user.id, user_data[12] + int(total_tokens))
        update_last_time_duration(message.from_user.id, user_data[11] + int(duration.total_seconds()))
        update_num_queries(message.from_user.id, user_data[13]+1)
        update_buffer_memory(message.from_user.id, pickle.dumps(memory))
        update_last_interaction(message.from_user.id, datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as error:
        await bot.send_message(message.from_user.id, f"ОШИБКА: {error}")
        logger.error(f"ОШИБКА generate_second_answer: {error}")

    await asyncio.sleep(1)


@router.message(F.text)
async def process_any_message(message: types.Message):
    await message.reply("Если не знаете что делать то нажмите завершить Консультацию или введите команду: /start")
    await asyncio.sleep(1)
