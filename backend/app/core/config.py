import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = "AI Website Builder"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    PROJECTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "projects")

settings = Settings()
os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
