# Начальные данные для навыков (потом можно расширить)

SKILL_ORDER = [
    "variables",
    "conditions",
    "loops",
    "strings_lists",
    "functions",
    "dicts_sets",
    "oop",
    "algorithms"
]

SKILL_TREE = {
    "variables": {
        "name": "🌱 Переменные и типы",
        "prerequisite": None,
        "theory": "📚 **Переменные и типы данных**\n\n"
                  "Переменная — это 'коробочка' для хранения данных.\n\n"
                  "Основные типы:\n"
                  "• `int` — целые числа: 1, 42, -7\n"
                  "• `float` — дробные: 3.14, -0.5\n"
                  "• `str` — строки: 'Привет', \"Python\"\n"
                  "• `bool` — True или False\n\n"
                  "Пример:\n"
                  "```python\n"
                  "name = 'Анна'\n"
                  "age = 25\n"
                  "pi = 3.14\n"
                  "is_student = True\n"
                  "```\n\n"
                  "Узнать тип: `type(переменная)`"
    },
    "conditions": {
        "name": "🔀 Условные операторы",
        "prerequisite": "variables",
        "theory": "📚 **Условия (if/elif/else)**\n\n"
                  "Позволяют программе принимать решения.\n\n"
                  "Операторы сравнения:\n"
                  "• `==` равно\n"
                  "• `!=` не равно\n"
                  "• `>` `<` `>=` `<=`\n\n"
                  "Логические операторы:\n"
                  "• `and` — И\n"
                  "• `or` — ИЛИ\n"
                  "• `not` — НЕ\n\n"
                  "Пример:\n"
                  "```python\n"
                  "age = 18\n"
                  "if age >= 18:\n"
                  "    print('Можно!')\n"
                  "else:\n"
                  "    print('Нельзя')\n"
                  "```"
    },
    "loops": {
        "name": "🔄 Циклы",
        "prerequisite": "conditions",
        "theory": "📚 **Циклы for и while**\n\n"
                  "`for` — когда знаем сколько раз повторять:\n"
                  "```python\n"
                  "for i in range(5):\n"
                  "    print(i)  # 0 1 2 3 4\n"
                  "```\n\n"
                  "`while` — пока условие истинно:\n"
                  "```python\n"
                  "x = 0\n"
                  "while x < 5:\n"
                  "    print(x)\n"
                  "    x += 1\n"
                  "```\n\n"
                  "• `break` — выход из цикла\n"
                  "• `continue` — пропуск итерации"
    },
    "strings_lists": {
        "name": "🎯 Строки и списки",
        "prerequisite": "loops",
        "theory": "📚 **Строки и списки**\n\n"
                  "Строка — последовательность символов:\n"
                  "```python\n"
                  "s = 'Python'\n"
                  "s[0]    # 'P'\n"
                  "s[1:4]  # 'yth'\n"
                  "len(s)  # 6\n"
                  "```\n\n"
                  "Список — изменяемая коллекция:\n"
                  "```python\n"
                  "lst = [1, 2, 3]\n"
                  "lst.append(4)\n"
                  "lst[0]  # 1\n"
                  "for x in lst:\n"
                  "    print(x)\n"
                  "```"
    },
    "functions": {
        "name": "🏗️ Функции",
        "prerequisite": "strings_lists",
        "theory": "📚 **Функции**\n\n"
                  "Блок кода, который можно вызывать много раз:\n\n"
                  "```python\n"
                  "def greet(name):\n"
                  "    return f'Привет, {name}!'\n\n"
                  "print(greet('Мир'))  # Привет, Мир!\n"
                  "```\n\n"
                  "• `def` — объявление\n"
                  "• `return` — возврат значения\n"
                  "• Аргументы по умолчанию: `def f(x=5)`"
    },
    "dicts_sets": {
        "name": "🧩 Словари и множества",
        "prerequisite": "functions",
        "theory": "📚 **Словари и множества**\n\n"
                  "Словарь — пары ключ-значение:\n"
                  "```python\n"
                  "d = {'name': 'Анна', 'age': 25}\n"
                  "d['name']  # 'Анна'\n"
                  "d['city'] = 'Москва'\n"
                  "```\n\n"
                  "Множество — уникальные элементы:\n"
                  "```python\n"
                  "s = {1, 2, 3, 3}  # {1, 2, 3}\n"
                  "s.add(4)\n"
                  "```"
    },
    "oop": {
        "name": "🔧 ООП",
        "prerequisite": "functions",
        "theory": "📚 **Объектно-ориентированное программирование**\n\n"
                  "Класс — шаблон для объектов:\n"
                  "```python\n"
                  "class Dog:\n"
                  "    def __init__(self, name):\n"
                  "        self.name = name\n"
                  "    \n"
                  "    def bark(self):\n"
                  "        return f'{self.name}: Гав!'\n\n"
                  "dog = Dog('Бобик')\n"
                  "print(dog.bark())\n"
                  "```\n\n"
                  "• `__init__` — конструктор\n"
                  "• `self` — ссылка на объект\n"
                  "• Наследование: `class Puppy(Dog)`"
    },
    "algorithms": {
        "name": "⚡ Алгоритмы",
        "prerequisite": "dicts_sets",
        "theory": "📚 **Базовые алгоритмы**\n\n"
                  "Сортировка:\n"
                  "```python\n"
                  "sorted([3,1,2])  # [1, 2, 3]\n"
                  "lst.sort()  # на месте\n"
                  "```\n\n"
                  "Поиск:\n"
                  "• Линейный: перебор всех элементов\n"
                  "• Бинарный: деление пополам\n\n"
                  "Рекурсия — функция вызывает саму себя:\n"
                  "```python\n"
                  "def fact(n):\n"
                  "    if n <= 1: return 1\n"
                  "    return n * fact(n-1)\n"
                  "```"
    }
}

TASKS = {
    "variables_1": {
        "skill": "variables",
        "difficulty": 1,
        "title": "Приветствие",
        "description": "Напиши программу, которая запрашивает имя пользователя и выводит 'Привет, [имя]!'",
        "test_cases": [
            {"input": "Анна\n", "expected": "Привет, Анна!\n"},
            {"input": "Иван\n", "expected": "Привет, Иван!\n"}
        ],
        "template": "name = input()\n# Твой код здесь\n",
        "hints": [
            "Используй input() для получения имени",
            "Соедини строки через + или f-строку"
        ]
    },
    "variables_2": {
        "skill": "variables",
        "difficulty": 2,
        "title": "Калькулятор возраста",
        "description": "Спроси год рождения и вычисли возраст (считаем что сейчас 2024 год)",
        "test_cases": [
            {"input": "2000\n", "expected": "24\n"},
            {"input": "1990\n", "expected": "34\n"}
        ],
        "template": "year = int(input())\n# Твой код здесь\n",
        "hints": ["Не забудь преобразовать input в число", "Вычти год из 2024"]
    },
    "variables_3": {
        "skill": "variables",
        "difficulty": 2,
        "title": "Обмен значений",
        "description": "Даны две переменные a и b. Поменяй их значения местами и выведи через пробел.",
        "test_cases": [
            {"input": "5 3\n", "expected": "3 5\n"},
            {"input": "1 100\n", "expected": "100 1\n"}
        ],
        "template": "data = input().split()\na = int(data[0])\nb = int(data[1])\n# Твой код здесь\n",
        "hints": [
            "Можно использовать временную переменную",
            "В Python можно сделать a, b = b, a"
        ]
    },
    "conditions_1": {
        "skill": "conditions",
        "difficulty": 1,
        "title": "Чётное или нечётное",
        "description": "Дано число. Выведи 'чётное' или 'нечётное'",
        "test_cases": [
            {"input": "4\n", "expected": "чётное\n"},
            {"input": "7\n", "expected": "нечётное\n"},
            {"input": "0\n", "expected": "чётное\n"}
        ],
        "template": "n = int(input())\n# Твой код здесь\n",
        "hints": ["Используй оператор % (остаток от деления)", "Чётное число делится на 2 без остатка"]
    },
    "conditions_2": {
        "skill": "conditions",
        "difficulty": 2,
        "title": "Оценка",
        "description": "Дано число баллов (0-100). Выведи оценку:\n90-100: 'Отлично'\n70-89: 'Хорошо'\n50-69: 'Удовлетворительно'\n0-49: 'Неудовлетворительно'",
        "test_cases": [
            {"input": "95\n", "expected": "Отлично\n"},
            {"input": "75\n", "expected": "Хорошо\n"},
            {"input": "60\n", "expected": "Удовлетворительно\n"},
            {"input": "30\n", "expected": "Неудовлетворительно\n"}
        ],
        "template": "score = int(input())\n# Твой код здесь\n",
        "hints": ["Используй if/elif/else", "Проверяй условия от большего к меньшему"]
    },
    "conditions_3": {
        "skill": "conditions",
        "difficulty": 3,
        "title": "Високосный год",
        "description": "Дан год. Определи, високосный ли он.\nПравила: год високосный если делится на 4, но не на 100, ИЛИ делится на 400",
        "test_cases": [
            {"input": "2024\n", "expected": "високосный\n"},
            {"input": "1900\n", "expected": "не високосный\n"},
            {"input": "2000\n", "expected": "високосный\n"},
            {"input": "2023\n", "expected": "не високосный\n"}
        ],
        "template": "year = int(input())\n# Твой код здесь\n",
        "hints": ["Используй % для проверки делимости", "Комбинируй условия через and и or"]
    },
    "loops_1": {
        "skill": "loops",
        "difficulty": 1,
        "title": "Сумма чисел",
        "description": "Дано число N. Выведи сумму чисел от 1 до N.",
        "test_cases": [
            {"input": "5\n", "expected": "15\n"},
            {"input": "10\n", "expected": "55\n"},
            {"input": "1\n", "expected": "1\n"}
        ],
        "template": "n = int(input())\n# Твой код здесь\n",
        "hints": ["Создай переменную-счётчик", "Используй цикл for с range(1, n+1)"]
    },
    "loops_2": {
        "skill": "loops",
        "difficulty": 2,
        "title": "Таблица умножения",
        "description": "Дано число. Выведи таблицу умножения для него от 1 до 10 (каждая строка: 'N x i = результат')",
        "test_cases": [
            {"input": "7\n", "expected": "7 x 1 = 7\n7 x 2 = 14\n7 x 3 = 21\n7 x 4 = 28\n7 x 5 = 35\n7 x 6 = 42\n7 x 7 = 49\n7 x 8 = 56\n7 x 9 = 63\n7 x 10 = 70\n"},
            {"input": "3\n", "expected": "3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n3 x 4 = 12\n3 x 5 = 15\n3 x 6 = 18\n3 x 7 = 21\n3 x 8 = 24\n3 x 9 = 27\n3 x 10 = 30\n"}
        ],
        "template": "n = int(input())\n# Твой код здесь\n",
        "hints": ["Используй for i in range(1, 11)", "Используй f-строку для форматирования"]
    },
    "loops_3": {
        "skill": "loops",
        "difficulty": 3,
        "title": "Поиск простых чисел",
        "description": "Дано число N. Выведи все простые числа от 2 до N (каждое на новой строке).\nПростое число — делится только на 1 и на себя.",
        "test_cases": [
            {"input": "10\n", "expected": "2\n3\n5\n7\n"},
            {"input": "20\n", "expected": "2\n3\n5\n7\n11\n13\n17\n19\n"},
            {"input": "2\n", "expected": "2\n"}
        ],
        "template": "n = int(input())\n# Твой код здесь\n",
        "hints": [
            "Используй вложенный цикл для проверки делителей",
            "Проверяй делители от 2 до sqrt(n)",
            "Используй флаг (булеву переменную)"
        ]
    }
}