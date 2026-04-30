import aiosqlite
from pathlib import Path

DB_PATH = Path("database/bot_database.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
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
            skill_name TEXT PRIMARY KEY,
            status TEXT DEFAULT 'locked',
            tasks_solved INTEGER DEFAULT 0,
            tasks_total INTEGER DEFAULT 3,
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