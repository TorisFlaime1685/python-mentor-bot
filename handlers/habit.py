import asyncio
import calendar
from datetime import datetime, date, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_db

router = Router()

# Храним какой месяц смотрит пользователь
user_calendar_view = {}

# Время напоминания
REMINDER_HOUR = 20


async def get_user_streaks(user_id: int):
    """Считает текущий стрик, лучший стрик, дни активности в этом месяце"""
    db = await get_db()
    rows = await db.execute(
        "SELECT date FROM daily_activity WHERE user_id = ? ORDER BY date ASC",
        (user_id,)
    )
    dates = [row["date"] for row in await rows.fetchall()]
    await db.close()

    if not dates:
        return 0, 0, []

    today = date.today()
    
    # Текущий стрик
    current_streak = 0
    check_date = today
    
    if today.isoformat() in dates:
        current_streak = 1
        check_date = today - timedelta(days=1)
        while check_date.isoformat() in dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    else:
        check_date = today - timedelta(days=1)
        if check_date.isoformat() in dates:
            current_streak = 1
            check_date -= timedelta(days=1)
            while check_date.isoformat() in dates:
                current_streak += 1
                check_date -= timedelta(days=1)

    # Лучший стрик
    sorted_dates = sorted([date.fromisoformat(d) for d in dates])
    best_streak = 0
    temp_streak = 1

    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            temp_streak += 1
        else:
            best_streak = max(best_streak, temp_streak)
            temp_streak = 1
    best_streak = max(best_streak, temp_streak, current_streak)

    # Активные дни в этом месяце
    active_days = []
    for d in sorted_dates:
        if d.year == today.year and d.month == today.month:
            active_days.append(d.day)

    return current_streak, best_streak, active_days


async def generate_calendar(year: int, month: int, active_days: list, today_date: date):
    """Рисует текстовый календарь"""
    month_names = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    
    cal = calendar.monthcalendar(year, month)
    
    lines = [f"📅 **{month_names[month]} {year}**", "", "Пн Вт Ср Чт Пт Сб Вс"]
    
    for week in cal:
        week_str = ""
        for day_num in week:
            if day_num == 0:
                week_str += "   "
            else:
                is_today = (today_date.year == year and today_date.month == month and today_date.day == day_num)
                is_active = day_num in active_days
                
                if is_today and is_active:
                    week_str += "✅ "
                elif is_today:
                    week_str += "🔵 "
                elif is_active:
                    week_str += "✅ "
                else:
                    week_str += "❌ "
        lines.append(week_str.rstrip())
    
    return "\n".join(lines)


@router.callback_query(F.data == "habit_tracker")
async def show_tracker(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_date = date.today()

    if user_id not in user_calendar_view:
        user_calendar_view[user_id] = {"year": today_date.year, "month": today_date.month}

    view = user_calendar_view[user_id]
    current_streak, best_streak, active_days = await get_user_streaks(user_id)
    calendar_text = await generate_calendar(view["year"], view["month"], active_days, today_date)

    # Мотивация
    if current_streak == 0:
        extra = "💤 Сегодня ещё не кодил. Самое время!"
    elif current_streak < 3:
        extra = "🌱 Хорошее начало!"
    elif current_streak < 7:
        extra = "🚀 Отличный стрик!"
    elif current_streak < 14:
        extra = "💪 Впечатляет!"
    elif current_streak < 30:
        extra = "🏅 Машина!"
    else:
        extra = "👑 Легенда!"

    if current_streak == best_streak and current_streak > 0:
        extra += "\n🎯 Ты повторяешь свой рекорд!"
    elif current_streak > best_streak and best_streak > 0:
        extra += "\n🎉 НОВЫЙ РЕКОРД!"

    text = (
        f"🔥 **Трекер привычки «Кодить каждый день»**\n\n"
        f"{calendar_text}\n\n"
        f"📊 Стрик: **{current_streak}** дн. | 🏆 Рекорд: **{best_streak}** дн.\n\n"
        f"{extra}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀", callback_data="habit_prev"),
            InlineKeyboardButton(text="Сегодня", callback_data="habit_today"),
            InlineKeyboardButton(text="▶", callback_data="habit_next"),
        ],
        [InlineKeyboardButton(text="📊 Статистика за год", callback_data="habit_year")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.in_(["habit_prev", "habit_next"]))
async def change_month(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_date = date.today()

    if user_id not in user_calendar_view:
        user_calendar_view[user_id] = {"year": today_date.year, "month": today_date.month}

    view = user_calendar_view[user_id]

    if callback.data == "habit_prev":
        if view["month"] == 1:
            view["month"] = 12
            view["year"] -= 1
        else:
            view["month"] -= 1
    else:
        if view["month"] == 12:
            view["month"] = 1
            view["year"] += 1
        else:
            view["month"] += 1

    current_streak, best_streak, active_days = await get_user_streaks(user_id)
    calendar_text = await generate_calendar(view["year"], view["month"], active_days, today_date)

    text = (
        f"🔥 **Трекер привычки**\n\n{calendar_text}\n\n"
        f"📊 Стрик: **{current_streak}** дн. | 🏆 Рекорд: **{best_streak}** дн."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀", callback_data="habit_prev"),
            InlineKeyboardButton(text="Сегодня", callback_data="habit_today"),
            InlineKeyboardButton(text="▶", callback_data="habit_next"),
        ],
        [InlineKeyboardButton(text="📊 Статистика за год", callback_data="habit_year")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "habit_today")
async def go_today(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_date = date.today()
    user_calendar_view[user_id] = {"year": today_date.year, "month": today_date.month}

    current_streak, best_streak, active_days = await get_user_streaks(user_id)
    calendar_text = await generate_calendar(today_date.year, today_date.month, active_days, today_date)

    text = (
        f"🔥 **Трекер привычки**\n\n{calendar_text}\n\n"
        f"📊 Стрик: **{current_streak}** дн. | 🏆 Рекорд: **{best_streak}** дн."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀", callback_data="habit_prev"),
            InlineKeyboardButton(text="Сегодня", callback_data="habit_today"),
            InlineKeyboardButton(text="▶", callback_data="habit_next"),
        ],
        [InlineKeyboardButton(text="📊 Статистика за год", callback_data="habit_year")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "habit_year")
async def year_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    today_date = date.today()

    db = await get_db()
    rows = await db.execute(
        "SELECT date, tasks_solved, xp_earned FROM daily_activity WHERE user_id = ? AND date LIKE ?",
        (user_id, f"{today_date.year}%")
    )
    rows = await rows.fetchall()
    await db.close()

    if not rows:
        text = "📊 За этот год пока нет данных."
    else:
        total_days = len(rows)
        total_tasks = sum(r["tasks_solved"] for r in rows)
        total_xp = sum(r["xp_earned"] for r in rows)

        month_names = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
        month_bars = ""

        for i, name in enumerate(month_names, 1):
            month_key = f"{today_date.year}-{i:02d}"
            days = sum(1 for r in rows if r["date"].startswith(month_key))
            bar = "█" * days + "░" * (31 - days)
            month_bars += f"{name}: {bar} ({days} дн.)\n"

        text = (
            f"📊 **Статистика за {today_date.year} год**\n\n"
            f"📅 Дней с кодом: **{total_days}**\n"
            f"🎯 Задач решено: **{total_tasks}**\n"
            f"⭐ Всего XP: **{total_xp}**\n\n"
            f"**Активность по месяцам:**\n{month_bars}"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К календарю", callback_data="habit_tracker")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Быстрый доступ по слову "стрик"
@router.message(F.text.lower().in_(["стрик", "привычка", "календарь", "трекер"]))
async def quick_habit(message: Message):
    user_id = message.from_user.id
    today_date = date.today()

    current_streak, best_streak, _ = await get_user_streaks(user_id)

    if current_streak == 0:
        status = "💤 Сегодня ещё не кодил. Самое время!"
    elif current_streak < 7:
        status = "🔥 Хороший стрик!"
    else:
        status = "👑 В ударе!"

    await message.answer(
        f"🔥 Стрик: **{current_streak}** дн. | 🏆 Рекорд: **{best_streak}** дн.\n{status}\n\n"
        "Подробнее: /menu → 🔥 Трекер привычки",
        parse_mode="Markdown"
    )