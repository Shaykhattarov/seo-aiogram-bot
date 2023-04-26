import config
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


from app import headers
