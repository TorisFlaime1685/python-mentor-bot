import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_EXECUTION_TIME = 3  # секунды на выполнение кода
FORBIDDEN_KEYWORDS = ["__import__", "eval(", "exec(", "open(", "os.", "sys.", "subprocess", "shutil", "importlib"]