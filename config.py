import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "ESEMentorAI2026"
DATABASE = "users.db"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")