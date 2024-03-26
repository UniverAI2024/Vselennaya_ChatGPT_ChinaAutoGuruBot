from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage


load_dotenv()

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
storage = MemoryStorage() #RedisStorage.from_url('redis://localhost:6379/1')

bot = Bot(token=TOKEN, parse_mode=None)
dp = Dispatcher(storage=storage)


