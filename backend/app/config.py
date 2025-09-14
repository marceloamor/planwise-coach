import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # Using GPT-4 for better plan generation
DB_URL = os.getenv("DB_URL", "sqlite:///./coach.db") 