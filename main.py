import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot_modules.notion.notion import Notion

from db import init_db


con, cur = init_db()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ["TG_BOT_TOKEN"])
dp = Dispatcher()
notion = Notion(cur, con, dp)


async def main():
    notion.set_routes()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
