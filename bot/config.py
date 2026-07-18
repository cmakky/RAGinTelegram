from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не найден."
    )

# Папка куда сохраняются файлы загруженные пользователями
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Папка куда сохраняется извлеченный текст
EXTRACTED_DIR = BASE_DIR / "storage" / "extracted"
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS_DIR = BASE_DIR / "storage" / "chunks"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1024 # Размер чанка в символах

CHUNK_OVERLAP = 128 # Перекрытие чанков

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"} # Какие расширения доступны для чтения

MAX_FILE_SIZE = 20971520 # Максимальный размер файла 20 МБ