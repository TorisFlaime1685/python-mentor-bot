import aiosqlite
from pathlib import Path
import os

# Используем постоянное хранилище Amvera если доступно
DATA_DIR = Path("/data") if os.path.exists("/data") else Path("database")
DB_PATH = DATA_DIR / "bot_database.db"

# Создаём папку если её нет
DATA_DIR.mkdir(parents=True, exist_ok=True)

async def get_db():
    """Получить соединение с БД"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    """Создать таблицы при первом запуске"""
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level TEXT DEFAULT 'beginner',
            xp INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_activity TEXT,
            current_skill TEXT DEFAULT 'variables'
        );

        CREATE TABLE IF NOT EXISTS skill_progress (
            user_id INTEGER,
            skill_name TEXT,
            status TEXT DEFAULT 'locked',
            tasks_solved INTEGER DEFAULT 0,
            tasks_total INTEGER DEFAULT 3,
            PRIMARY KEY (user_id, skill_name),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );

        CREATE TABLE IF NOT EXISTS solved_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id TEXT,
            solved_at TEXT,
            attempts INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );

        CREATE TABLE IF NOT EXISTS daily_activity (
            user_id INTEGER,
            date TEXT,
            tasks_solved INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, date),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
    """)
    await db.commit()
    await db.close()