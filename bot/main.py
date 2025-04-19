# bot/main.py

import asyncio
import logging
from aiogram import Dispatcher
from bot.loader import bot, dp
from bot.handlers.start import router as start_router
from bot.handlers.photo import router as photo_router
from bot.handlers.video import router as video_router
from bot.handlers.admin import router as admin_router

logging.basicConfig(level=logging.DEBUG)

async def main():
    # 👇 Регистрируем все обработчики
    dp.include_router(start_router)
    dp.include_router(photo_router)
    dp.include_router(video_router)
    dp.include_router(admin_router)

    print("🤖 Бот запущен и ждёт команд...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
