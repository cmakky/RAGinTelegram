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

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY не найдет."
    )

GROQ_MODEL = "openai/gpt-oss-20b"

# Папка куда сохраняются файлы загруженные пользователями
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Папка куда сохраняется извлеченный текст
EXTRACTED_DIR = BASE_DIR / "storage" / "extracted"
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

# Папка где сохраняются чанки (разбитый текст)
CHUNKS_DIR = BASE_DIR / "storage" / "chunks"
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

# Папка для хранилища векторной базы
VECTOR_DB_DIR = BASE_DIR / "storage" / "vectordb"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Хранить ли оригинальный файл после того как текст излвечен.
# По умолчанию False, можно поменять если нужно хранить.
KEEP_UPLOADED_FILES = False

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

CHUNK_SIZE = 1024 # Размер чанка в символах

CHUNK_OVERLAP = 128 # Перекрытие чанков

TOP_K_RESULTS = 3 # Кол-во ближайших чанков по вопросу пользователя

SIMILARITY_THRESHOLD = 0.42 # Порог релевантности

MAX_HISTORY_EXCHANGES = 3 # Сколько последних сообщений хранится как контекст

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"} # Какие расширения доступны для чтения

MAX_FILE_SIZE = 20971520 # Максимальный размер файла 20 МБ