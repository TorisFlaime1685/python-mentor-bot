from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_db, init_db
from datetime import datetime

router = Router()

class Onboarding(StatesGroup):
    choosing_level = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await init_db()
    
    user_id = message.from_user.id
    db = await get_db()
    user = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = await user.fetchone()
    await db.close()

    if user:
        await show_main_menu(message)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌱 Совсем новичок (базовый Python)", callback_data="level_beginner")],
            [InlineKeyboardButton(text="🌿 Знаю основы (циклы, функции)", callback_data="level_intermediate")],
            [InlineKeyboardButton(text="🌳 Уверенный (ООП, алгоритмы)", callback_data="level_advanced")]
        ])
        await message.answer(
            "👋 Привет! Я твой ментор по Python! 🐍\n\n"
            "Я помогу тебе изучить программирование шаг за шагом.\n\n"
            "📋 Что я умею:\n"
            "• Обучаю по проверенной программе\n"
            "• Даю задачи с автопроверкой\n"
            "• Разбираю твой код и нахожу ошибки\n"
            "• Отслеживаю твой прогресс\n"
            "• Мотивирую не сдаваться! 💪\n\n"
            "Для начала выбери свой уровень:",
            reply_markup=keyboard
        )
        await state.set_state(Onboarding.choosing_level)

@router.callback_query(Onboarding.choosing_level)
async def process_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.replace("level_", "")
    user_id = callback.from_user.id

    # Определяем начальный скилл в зависимости от уровня
    start_skill = {
        "beginner": "variables",
        "intermediate": "strings_lists",
        "advanced": "oop"
    }

    db = await get_db()
    await db.execute(
        "INSERT INTO users (user_id, username, level, current_skill) VALUES (?, ?, ?, ?)",
        (user_id, callback.from_user.username, level, start_skill[level])
    )
    
    # Инициализируем скиллы
    from data.tasks import SKILL_ORDER
    unlock = True
    for skill in SKILL_ORDER:
        status = 'unlocked' if unlock else 'locked'
        await db.execute(
            "INSERT OR IGNORE INTO skill_progress (user_id, skill_name, status) VALUES (?, ?, ?)",
            (user_id, skill, status)
        )
        if skill == start_skill[level]:
            unlock = True
    
    await db.commit()
    await db.close()

    await callback.message.answer(
        "🎉 Отлично! Профиль создан!\n\n"
        "📚 Сейчас открою меню — начнём обучение!\n"
        "Рекомендую сразу нажать 🌳 Дерево навыков чтобы увидеть свой путь."
    )
    await callback.answer()
    await state.clear()
    await show_main_menu(callback.message)

async def show_main_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌳 Дерево навыков", callback_data="skill_tree")],
        [InlineKeyboardButton(text="📖 Теория", callback_data="theory")],
        [InlineKeyboardButton(text="🎯 Получить задачу", callback_data="get_task")],
        [InlineKeyboardButton(text="🔧 Разбор кода", callback_data="review_info")],
        [InlineKeyboardButton(text="🔥 Трекер привычки", callback_data="habit_tracker")],
        [InlineKeyboardButton(text="🧩 Загадки кода", callback_data="puzzles_menu")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])
    await message.answer("📋 Главное меню\nВыбери действие:", reply_markup=keyboard)

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await show_main_menu(message)

@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: CallbackQuery):
    await show_main_menu(callback.message)
    await callback.answer()

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = (
        "🤖 **Как пользоваться ботом:**\n\n"
        "1️⃣ Начни с 🌳 Дерева навыков — посмотри что будешь изучать\n"
        "2️⃣ Читай 📖 Теорию по текущей теме\n"
        "3️⃣ Бери 🎯 Задачу и пробуй решить\n"
        "4️⃣ Отправляй код прямо в чат — я проверю\n"
        "5️⃣ Если застрял — используй подсказки\n"
        "6️⃣ Отмечай прогресс в 👤 Профиле\n\n"
        "Также можешь отправить любой код и я разберу его в 🔧 Разборе кода\n\n"
        "Команды:\n"
        "/start — перезапуск\n"
        "/menu — главное меню\n"
        "/profile — профиль\n"
        "/skip — пропустить задачу"
    )
    await callback.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()