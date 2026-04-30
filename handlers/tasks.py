from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.code_executor import execute_code_safely
import traceback

router = Router()

class Review(StatesGroup):
    waiting_for_code = State()

CODE_PATTERNS = {
    "print_without_parens": {
        "pattern": "print [^(]",
        "error": "В Python 3 `print` — функция, нужны скобки: `print(...)`",
    },
    "assignment_in_if": {
        "pattern": "if .+ = .+",
        "error": "В условии `if` используй `==` для сравнения, а не `=` (присваивание)",
    },
    "missing_colon": {
        "pattern": "(if|for|while|def) .+[^:]$",
        "error": "После `if/for/while/def` нужно двоеточие `:`",
    },
    "indentation_error": {
        "pattern": None,  # Определяется при выполнении
        "error": "Ошибка отступов. В Python отступы важны! Используй 4 пробела или Tab для вложенных блоков.",
    }
}

@router.callback_query(F.data == "review_info")
async def review_info(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Review.waiting_for_code)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        "🔧 **Разбор кода**\n\n"
        "Отправь мне свой Python-код, и я:\n"
        "• Проверю его на ошибки\n"
        "• Найду типичные проблемы новичков\n"
        "• Подскажу как улучшить\n"
        "• Проверю стиль кода\n\n"
        "Просто отправь код сообщением 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Review.waiting_for_code)
async def analyze_code(message: Message, state: FSMContext):
    user_code = message.text
    
    # Извлекаем код из ``` если есть
    if "```" in user_code:
        lines = user_code.split("\n")
        code_lines = []
        in_code = False
        for line in lines:
            if "```" in line:
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
        user_code = "\n".join(code_lines)

    if not user_code.strip():
        await message.answer("Отправь код для анализа")
        return

    # Анализ кода
    issues = []
    suggestions = []

    # Проверка на пустой код
    if len(user_code.strip()) < 5:
        await message.answer("Код слишком короткий для анализа. Отправь хотя бы несколько строк.")
        return

    # Проверка длины строк
    lines = user_code.split("\n")
    for i, line in enumerate(lines):
        if len(line) > 79:
            issues.append(f"Строка {i+1}: слишком длинная ({len(line)} символов). PEP 8 рекомендует до 79.")

    # Проверка на использование input() без int()
    if "input()" in user_code and "int(input())" not in user_code and "float(input())" not in user_code:
        if "+" in user_code or "-" in user_code or "*" in user_code or "/" in user_code:
            suggestions.append("💡 Если работаешь с числами, оберни `input()` в `int()` или `float()`")

    # Проверка на смешивание табов и пробелов
    if "\t" in user_code and "    " in user_code:
        issues.append("⚠️ Смешаны табуляции и пробелы. Используй что-то одно (лучше пробелы)")

    # Проверка на == None вместо is None
    if "== None" in user_code:
        suggestions.append("💡 Вместо `== None` лучше использовать `is None`")

    # Запуск кода для поиска ошибок времени выполнения
    test_result = await execute_code_safely(user_code)
    
    if not test_result["success"]:
        error_output = test_result["output"]
        
        # Анализируем тип ошибки
        if "NameError" in error_output:
            var_name = ""
            if "'" in error_output:
                var_name = error_output.split("'")[1]
            issues.append(f"❌ NameError: переменная `{var_name}` не определена. Проверь правильность имени.")
        elif "TypeError" in error_output:
            issues.append("❌ TypeError: несовместимые типы данных. Проверь, что складываешь строку со строкой, число с числом.")
        elif "SyntaxError" in error_output:
            issues.append("❌ SyntaxError: синтаксическая ошибка. Проверь скобки, кавычки, двоеточия.")
        elif "IndentationError" in error_output:
            issues.append("❌ IndentationError: ошибка отступов. Вложенные блоки должны иметь одинаковый отступ.")
        elif "IndexError" in error_output:
            issues.append("❌ IndexError: выход за границы списка/строки. Проверь индексы.")
        elif "ValueError" in error_output:
            issues.append("❌ ValueError: неверное значение. Возможно, пытаешься превратить буквы в число.")
        else:
            issues.append(f"❌ Ошибка выполнения:\n```\n{error_output[:300]}\n```")
    else:
        suggestions.append("✅ Код выполняется без ошибок!")

    # Проверка на отсутствие комментариев
    if "#" not in user_code and len(lines) > 5:
        suggestions.append("💡 Добавь комментарии — они помогут понять код через неделю")

    # Проверка на использование list comprehension вместо цикла
    if "for" in user_code and ".append" in user_code:
        suggestions.append("💡 Возможно, здесь можно использовать list comprehension для краткости")

    # Формируем ответ
    response = "🔧 **Результат анализа:**\n\n"
    
    if issues:
        response += "⚠️ **Найденные проблемы:**\n"
        for issue in issues:
            response += f"• {issue}\n"
        response += "\n"

    if suggestions:
        response += "💡 **Советы по улучшению:**\n"
        for suggestion in suggestions:
            response += f"• {suggestion}\n"
        response += "\n"

    if not issues and not suggestions:
        response += "Код выглядит неплохо, но я не могу найти очевидных проблем без тестов.\n"

    response += "📊 **Быстрая проверка:**\n"
    if test_result["success"]:
        response += "✅ Выполняется без ошибок\n"
        if test_result["output"]:
            response += f"📤 Вывод: `{test_result['output'][:100]}`\n"
    else:
        response += "❌ Есть ошибки\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Анализировать другой код", callback_data="review_another")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    await message.answer(response, reply_markup=keyboard, parse_mode="Markdown")
    await state.clear()

@router.callback_query(F.data == "review_another")
async def review_another(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Review.waiting_for_code)
    await callback.message.answer("Отправь новый код для анализа")
    await callback.answer()

@router.callback_query(F.data == "review_my_code")
async def review_my_code(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Review.waiting_for_code)
    await callback.message.answer(
        "🔧 Отправь свой код (тот же или исправленный), я разберу его"
    )
    await callback.answer()