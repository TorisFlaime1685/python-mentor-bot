from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_db
from datetime import datetime
import random
import asyncio

router = Router()

class PuzzleState(StatesGroup):
    waiting_for_answer = State()

# Хранилище для активных «загадок» у пользователей
active_puzzles = {}

# -------------------------------------------------------------------
# База вопросов
# -------------------------------------------------------------------

QUIZ_QUESTIONS = [
    {
        "id": "quiz_1",
        "type": "quiz",
        "code": "x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
        "options": ["[1, 2, 3]", "[1, 2, 3, 4]", "Ошибка", "[1, 2, 3, 4, 4]"],
        "correct": 1, # индекс верного ответа
        "explanation": "y = x не создаёт новый список, а даёт второе имя тому же. Изменив y, ты изменил и x.",
        "xp": 5
    },
    {
        "id": "quiz_2",
        "type": "quiz",
        "code": "print(0.1 + 0.2 == 0.3)",
        "options": ["True", "False", "Ошибка"],
        "correct": 1,
        "explanation": "Из-за неточности чисел с плавающей точкой 0.1 + 0.2 будет 0.30000000000000004, что не равно 0.3.",
        "xp": 10
    },
    {
        "id": "quiz_3",
        "type": "quiz",
        "code": "a = (1, 2)\na[0] = 5\nprint(a)",
        "options": ["(1, 2)", "(5, 2)", "Ошибка", "(5, 2, 5)"],
        "correct": 2,
        "explanation": "Кортеж (tuple) — неизменяемый тип данных. Попытка присвоить a[0] = 5 вызовет TypeError.",
        "xp": 7
    },
    {
        "id": "quiz_4",
        "type": "quiz",
        "code": "print(bool([]))",
        "options": ["True", "False", "Ошибка", "None"],
        "correct": 1,
        "explanation": "Пустой список [] в Python считается «ложным» (falsy), поэтому bool([]) будет False.",
        "xp": 5
    },
    {
        "id": "quiz_5",
        "type": "quiz",
        "code": "def func(x=[]):\n    x.append(1)\n    return x\nprint(func())\nprint(func())",
        "options": ["[1] и [1]", "[1] и [1, 1]", "Ошибка", "[1] и [1] но по-другому"],
        "correct": 1,
        "explanation": "Изменяемые аргументы по умолчанию создаются ОДИН раз. Второй вызов добавит ещё одну 1 в тот же список.",
        "xp": 12
    }
]

DEBUG_QUESTIONS = [
    {
        "id": "debug_1",
        "type": "debug",
        "code": "def divide(a, b):\n    return a / b\nprint(divide(5, 0))",
        "answer_keywords": ["ZeroDivisionError", "деление на ноль", "деление на 0", "на ноль", "division by zero"],
        "correct_answer": "ZeroDivisionError: деление на ноль",
        "explanation": "На ноль делить нельзя! Ошибка ZeroDivisionError. Нужно добавить проверку: если b == 0, возвращать ошибку или специальное значение.",
        "xp": 8
    },
    {
        "id": "debug_2",
        "type": "debug",
        "code": "name = input('Имя: ')\nprint('Привет, ' + name)\n# Ошибка на строке с print",
        "answer_keywords": ["ничего", "нет ошибки", "всё правильно", "нет бага", "работает", "нету ошибки"],
        "correct_answer": "Код рабочий, ошибок нет",
        "explanation": "Хитрость! Код написан без ошибок. Иногда кажется что ошибка есть, но её нет 😏",
        "xp": 5
    },
    {
        "id": "debug_3",
        "type": "debug",
        "code": "for i in range(5)\n    print(i)",
        "answer_keywords": ["SyntaxError", "двоеточие", "colon", "синтаксическая", ":"],
        "correct_answer": "SyntaxError: пропущено двоеточие после range(5)",
        "explanation": "После range(5) должно быть двоеточие: `for i in range(5):`. Python использует : чтобы обозначить начало блока.",
        "xp": 6
    },
    {
        "id": "debug_4",
        "type": "debug",
        "code": "x = '5'\ny = 3\nprint(x + y)",
        "answer_keywords": ["TypeError", "типы", "строка", "число", "конкатенация", "int", "type"],
        "correct_answer": "TypeError: нельзя сложить строку и число",
        "explanation": "x — строка ('5'), y — число (3). Python не знает что делать. Нужно привести к одному типу: int(x) + y или x + str(y).",
        "xp": 7
    },
    {
        "id": "debug_5",
        "type": "debug",
        "code": "my_list = [1, 2, 3]\nprint(my_list[3])",
        "answer_keywords": ["IndexError", "индекс", "за границы", "выход", "list index out of range", "3"],
        "correct_answer": "IndexError: индекс 3 выходит за границы списка",
        "explanation": "В списке [1, 2, 3] элементы имеют индексы 0, 1, 2. Индекса 3 не существует. Нужно my_list[2] для последнего элемента.",
        "xp": 6
    },
    {
        "id": "debug_6",
        "type": "debug",
        "code": "def greet():\nprint('Привет!')\ngreet()",
        "answer_keywords": ["IndentationError", "отступ", "indent", "пробел"],
        "correct_answer": "IndentationError: нет отступа у print",
        "explanation": "После двоеточия в функции нужен отступ. Правильно:\ndef greet():\n    print('Привет!')",
        "xp": 6
    }
]

# -------------------------------------------------------------------
# Основная логика
# -------------------------------------------------------------------

async def add_xp(user_id: int, amount: int):
    """Начисляет XP пользователю и обновляет таблицы"""
    db = await get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    await db.execute(
        "UPDATE users SET xp = xp + ?, last_activity = ? WHERE user_id = ?",
        (amount, today, user_id)
    )
    await db.execute(
        "INSERT INTO daily_activity (user_id, date, tasks_solved, xp_earned) VALUES (?, ?, 1, ?) "
        "ON CONFLICT(user_id, date) DO UPDATE SET xp_earned = xp_earned + ?",
        (user_id, today, amount, amount)
    )
    await db.commit()
    await db.close()


# -------------------------------------------------------------------
# Меню загадок
# -------------------------------------------------------------------

@router.callback_query(F.data == "puzzles_menu")
async def show_puzzles_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤔 Угадай вывод", callback_data="puzzle_quiz")],
        [InlineKeyboardButton(text="🐛 Найди баг", callback_data="puzzle_debug")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    text = (
        "🧩 **Загадки кода**\n\n"
        "Выбери режим:\n"
        "🤔 **Угадай вывод** — покажу код и варианты, угадай что выведется\n"
        "🐛 **Найди баг** — покажу код с ошибкой, опиши что не так"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


# -------------------------------------------------------------------
# Угадай вывод
# -------------------------------------------------------------------

@router.callback_query(F.data == "puzzle_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    # Выбираем случайный вопрос, который пользователь ещё не решил
    db = await get_db()
    solved = await db.execute(
        "SELECT task_id FROM solved_tasks WHERE user_id = ? AND task_id LIKE 'quiz_%'",
        (user_id,)
    )
    solved_ids = [row["task_id"] for row in await solved.fetchall()]
    await db.close()
    
    available = [q for q in QUIZ_QUESTIONS if q["id"] not in solved_ids]
    
    if not available:
        await callback.message.edit_text(
            "🎉 Ты разгадал все загадки! Возвращайся позже — добавлю новые.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")]
            ])
        )
        await callback.answer()
        return
    
    question = random.choice(available)
    active_puzzles[user_id] = question
    
    # Формируем кнопки с вариантами
    buttons = []
    for i, option in enumerate(question["options"]):
        buttons.append([InlineKeyboardButton(
            text=option, 
            callback_data=f"quiz_answer_{i}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")])
    
    code_display = question["code"].replace("<", "&lt;").replace(">", "&gt;")
    
    text = (
        f"🤔 **Угадай вывод**\n\n"
        f"```python\n{question['code']}\n```\n\n"
        f"Что выведет этот код? Выбери вариант:"
    )
    
    await callback.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )
    await state.set_state(PuzzleState.waiting_for_answer)
    await callback.answer()


@router.callback_query(F.data.startswith("quiz_answer_"))
async def check_quiz_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    question = active_puzzles.get(user_id)
    
    if not question:
        await callback.answer("Вопрос устарел. Начни новый!")
        return
    
    user_choice = int(callback.data.replace("quiz_answer_", ""))
    correct = question["correct"]
    
    if user_choice == correct:
        # Правильно!
        xp = question["xp"]
        await add_xp(user_id, xp)
        
        # Запоминаем что решил
        db = await get_db()
        await db.execute(
            "INSERT INTO solved_tasks (user_id, task_id, solved_at) VALUES (?, ?, ?)",
            (user_id, question["id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        await db.commit()
        await db.close()
        
        text = (
            f"✅ **Правильно!** +{xp} XP\n\n"
            f"📝 Объяснение: {question['explanation']}"
        )
    else:
        correct_option = question["options"][correct]
        text = (
            f"❌ **Неверно!**\n\n"
            f"Ты выбрал: {question['options'][user_choice]}\n"
            f"Правильный ответ: **{correct_option}**\n\n"
            f"📝 Объяснение: {question['explanation']}"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤔 Ещё загадку", callback_data="puzzle_quiz")],
        [InlineKeyboardButton(text="🐛 Найди баг", callback_data="puzzle_debug")],
        [InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")]
    ])
    
    # Удаляем решённую загадку из активных
    active_puzzles.pop(user_id, None)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.clear()
    await callback.answer()


# -------------------------------------------------------------------
# Найди баг
# -------------------------------------------------------------------

@router.callback_query(F.data == "puzzle_debug")
async def start_debug(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    db = await get_db()
    solved = await db.execute(
        "SELECT task_id FROM solved_tasks WHERE user_id = ? AND task_id LIKE 'debug_%'",
        (user_id,)
    )
    solved_ids = [row["task_id"] for row in await solved.fetchall()]
    await db.close()
    
    available = [q for q in DEBUG_QUESTIONS if q["id"] not in solved_ids]
    
    if not available:
        await callback.message.edit_text(
            "🎉 Ты нашёл все баги! Возвращайся позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")]
            ])
        )
        await callback.answer()
        return
    
    question = random.choice(available)
    active_puzzles[user_id] = question
    
    text = (
        f"🐛 **Найди баг**\n\n"
        f"```python\n{question['code']}\n```\n\n"
        f"✏️ **Опиши ошибку** — напиши ответ текстом.\n"
        f"Например: «SyntaxError: пропущена скобка» или «деление на ноль»"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(PuzzleState.waiting_for_answer)
    await callback.answer()


@router.message(PuzzleState.waiting_for_answer)
async def check_debug_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    question = active_puzzles.get(user_id)
    
    # Проверяем, может это ответ на quiz (обрабатывается колбэком)
    if not question or question["type"] == "quiz":
        await message.answer("Начни загадку заново из меню.")
        await state.clear()
        return
    
    user_answer = message.text.lower().strip()
    
    # Проверяем по ключевым словам
    is_correct = any(keyword.lower() in user_answer for keyword in question["answer_keywords"])
    
    if is_correct:
        xp = question["xp"]
        await add_xp(user_id, xp)
        
        db = await get_db()
        await db.execute(
            "INSERT INTO solved_tasks (user_id, task_id, solved_at) VALUES (?, ?, ?)",
            (user_id, question["id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        await db.commit()
        await db.close()
        
        text = (
            f"✅ **Верно!** +{xp} XP\n\n"
            f"📝 {question['explanation']}"
        )
    else:
        text = (
            f"❌ **Не совсем!**\n\n"
            f"Твой ответ: «{message.text}»\n"
            f"Правильный ответ: **{question['correct_answer']}**\n\n"
            f"📝 {question['explanation']}"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐛 Ещё баг", callback_data="puzzle_debug")],
        [InlineKeyboardButton(text="🤔 Угадай вывод", callback_data="puzzle_quiz")],
        [InlineKeyboardButton(text="🔙 К загадкам", callback_data="puzzles_menu")]
    ])
    
    active_puzzles.pop(user_id, None)
    await message.answer(text, reply_markup=keyboard)
    await state.clear()