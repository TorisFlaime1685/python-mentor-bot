from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_db
from data.tasks import SKILL_TREE, SKILL_ORDER

router = Router()

@router.callback_query(F.data == "skill_tree")
async def show_skill_tree(callback: CallbackQuery):
    user_id = callback.from_user.id
    db = await get_db()
    
    skills = await db.execute(
        "SELECT * FROM skill_progress WHERE user_id = ? ORDER BY skill_name",
        (user_id,)
    )
    skills = await skills.fetchall()
    await db.close()

    skill_dict = {s["skill_name"]: s for s in skills} if skills else {}

    keyboard = []
    for skill_key in SKILL_ORDER:
        skill_data = SKILL_TREE.get(skill_key)
        if not skill_data:
            continue
            
        if skill_key in skill_dict:
            status = skill_dict[skill_key]["status"]
            tasks_solved = skill_dict[skill_key]["tasks_solved"]
            tasks_total = skill_dict[skill_key]["tasks_total"]
            
            if status == "completed":
                icon = "✅"
            elif status == "unlocked":
                icon = "🔓"
            else:
                icon = "🔒"
            
            text = f"{icon} {skill_data['name']} ({tasks_solved}/{tasks_total})"
        else:
            text = f"🔒 {skill_data['name']} (0/3)"
        
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"skill_{skill_key}")])

    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])

    await callback.message.edit_text(
        "🌳 **Дерево навыков**\n\n"
        "Проходи навыки по порядку. Чтобы открыть следующий, нужно решить 3 задачи в текущем.\n\n"
        "🔒 — закрыто\n"
        "🔓 — доступно\n"
        "✅ — пройдено",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("skill_"))
async def show_skill_info(callback: CallbackQuery):
    skill_key = callback.data.replace("skill_", "")
    skill_data = SKILL_TREE.get(skill_key)
    
    if not skill_data:
        await callback.answer("Навык не найден")
        return

    user_id = callback.from_user.id
    db = await get_db()
    progress = await db.execute(
        "SELECT * FROM skill_progress WHERE user_id = ? AND skill_name = ?",
        (user_id, skill_key)
    )
    progress = await progress.fetchone()
    await db.close()

    if progress and progress["status"] == "locked":
        prerequisite = skill_data.get("prerequisite")
        prereq_name = SKILL_TREE.get(prerequisite, {}).get("name", prerequisite) if prerequisite else "начало"
        await callback.answer(f"Сначала пройди: {prereq_name}")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Читать теорию", callback_data=f"theory_{skill_key}")],
        [InlineKeyboardButton(text="🎯 Решать задачи", callback_data=f"task_{skill_key}")],
        [InlineKeyboardButton(text="🔙 К дереву навыков", callback_data="skill_tree")]
    ])

    status_text = ""
    if progress:
        status_text = f"\n\n📊 Прогресс: {progress['tasks_solved']}/{progress['tasks_total']} задач решено"

    await callback.message.edit_text(
        f"{skill_data['name']}{status_text}\n\n"
        "Выбери действие:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data == "theory")
async def show_theory_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    db = await get_db()
    user = await db.execute("SELECT current_skill FROM users WHERE user_id = ?", (user_id,))
    user = await user.fetchone()
    await db.close()

    current_skill = user["current_skill"] if user else "variables"
    skill_data = SKILL_TREE.get(current_skill)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Текущая тема", callback_data=f"theory_{current_skill}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        "📚 **Теория**\n\n"
        f"Твоя текущая тема: {skill_data['name'] if skill_data else current_skill}\n\n"
        "Можешь прочитать теорию по текущей теме или вернуться.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("theory_"))
async def show_theory(callback: CallbackQuery):
    skill_key = callback.data.replace("theory_", "")
    skill_data = SKILL_TREE.get(skill_key)

    if not skill_data:
        await callback.answer("Теория не найдена")
        return

    user_id = callback.from_user.id
    db = await get_db()
    await db.execute(
        "UPDATE users SET current_skill = ? WHERE user_id = ?",
        (skill_key, user_id)
    )
    await db.commit()
    await db.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Решать задачи", callback_data=f"task_{skill_key}")],
        [InlineKeyboardButton(text="🔙 К навыку", callback_data=f"skill_{skill_key}")]
    ])

    await callback.message.edit_text(
        skill_data["theory"],
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()