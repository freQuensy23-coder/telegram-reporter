import asyncio
import os

import aiogram
import loguru
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

import usecase
from models import User, db
from scheduler import setup_scheduler

dp = Dispatcher()
bot = Bot(token=str(os.getenv("TELEGRAM_BOT_TOKEN")))


@dp.message(F.text.len() > 32 and F.text.contains("#done"))
async def process_message(message: Message):
    if message.from_user:
        loguru.logger.info(
            f"Message received: {message.text} from {message.from_user.username}"
        )
        await usecase.process_message(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            message=message.text or "",
            chat_id=message.chat.id,
        )


async def main():
    scheduler = setup_scheduler()
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
