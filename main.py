# TODO: запустить БД через Docker, инициализировать таблицы
import asyncio
import logging
from aiogram import Bot, Dispatcher

from db import init_db


con, cur = init_db()
logging.basicConfig(level=logging.INFO)

bot = Bot(token="12345678:AaBbCcDdEeFfGgHh")
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
