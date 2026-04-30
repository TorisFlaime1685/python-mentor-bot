import sys
import io
import traceback
import asyncio
from config import FORBIDDEN_KEYWORDS

async def execute_code_safely(code: str, test_input: str = None) -> dict:
    """
    Безопасно выполняет Python-код в изолированном пространстве имён.
    Возвращает словарь с результатом.
    """
    # Проверка на запрещённые ключевые слова
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in code:
            return {
                "success": False,
                "output": f"⛔ Запрещённая операция: использование {keyword}",
                "error": "forbidden"
            }

    # Перехватываем stdout
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    sys.stdout = io.StringIO()
    
    if test_input:
        sys.stdin = io.StringIO(test_input)

    # Ограниченное пространство имён
    restricted_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "int": int,
            "str": str,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "type": type,
            "isinstance": isinstance,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "input": input,
            "round": round,
            "pow": pow,
            "divmod": divmod,
            "ord": ord,
            "chr": chr,
            "str.lower": str.lower,
            "str.upper": str.upper,
            "str.split": str.split,
            "str.join": str.join,
            "str.replace": str.replace,
            "str.strip": str.strip,
            "str.startswith": str.startswith,
            "str.endswith": str.endswith,
            "list.append": list.append,
            "list.sort": list.sort,
            "list.pop": list.pop,
        }
    }

    result = {"success": False, "output": "", "error": None}

    try:
        # Запуск с таймаутом
        exec_globals = restricted_globals.copy()
        await asyncio.wait_for(
            asyncio.to_thread(exec, code, exec_globals),
            timeout=3.0
        )
        result["success"] = True
        result["output"] = sys.stdout.getvalue()
    except asyncio.TimeoutError:
        result["output"] = "⏰ Время выполнения истекло (3 секунды)"
        result["error"] = "timeout"
    except Exception as e:
        result["output"] = traceback.format_exc()
        result["error"] = str(type(e).__name__)
    finally:
        sys.stdout = old_stdout
        sys.stdin = old_stdin

    return result