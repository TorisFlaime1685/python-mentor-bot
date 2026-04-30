from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_db
from datetime import datetime

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    db = await get_db()

    user = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = await user.fetchone()

    skills = await db.execute(
        "SELECT * FROM skill_progress WHERE user_id = ?",
        (user_id,)
    )
    skills = await skills.fetchall()

    solved = await db.execute(
        "SELECT COUNT(*) as count FROM solved_tasks WHERE user_id = ?",
        (user_id,)
    )
    solved_count = (await solved.fetchone())["count"]

    # Подсчёт дневной активности
    today = datetime.now().strftime("%Y-%m-%d")
    today_activity = await db.execute(
        "SELECT * FROM daily_activity WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    today_activity = await today_activity.fetchone()

    await db.close()

    unlocked = sum(1 for s in skills if s["status"] == "unlocked")
    completed = sum(1 for s in skills if s["status"] == "completed")

    level_emoji = {"beginner": "🌱", "intermediate": "🌿", "advanced": "🌳"}

    profile_text = (
        f"{level_emoji.get(user['level'], '🌱')} **Твой профиль**\n\n"
        f"📊 **Уровень:** {user['level']}\n"
        f"⭐ **XP:** {user['xp']}\n"
        f"🔥 **Дней подряд:** {user['streak']}\n"
        f"✅ **Решено задач:** {solved_count}\n"
        f"📚 **Навыков открыто:** {unlocked}/8\n"
        f"🏆 **Навыков пройдено:** {completed}/8\n\n"
        f"📅 **Сегодня:** {today_activity['tasks_solved'] if today_activity else 0} задач, "
        f"{today_activity['xp_earned'] if today_activity else 0} XP"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(profile_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()