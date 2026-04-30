import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.habit import router as habit_router
from handlers.puzzles import router as puzzles_router 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    from handlers.start import router as start_router
    from handlers.profile import router as profile_router
    from handlers.learn import router as learn_router
    from handlers.tasks import router as tasks_router
    from handlers.code_review import router as review_router

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(learn_router)
    dp.include_router(tasks_router)
    dp.include_router(review_router)
    dp.include_router(habit_router) 
    dp.include_router(puzzles_router) 

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())