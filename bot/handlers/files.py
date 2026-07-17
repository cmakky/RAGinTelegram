import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message

from bot.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOADS_DIR, EXTRACTED_DIR
from bot.services.text_extraction import extract_text, ExtractionError

router = Router(name="files")
logger = logging.getLogger(__name__)


def user_dir(user_id: int) -> Path:
    """Возвращает папку для файлов конкретного пользователя."""
    path = UPLOADS_DIR / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_extracted_dir(user_id: int) -> Path:
    """Возвращает папку для извлеченного текста пользователя."""
    path = EXTRACTED_DIR / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.message(F.document)
async def handle_document(message: Message) -> None:
    doc = message.document
    file_name = doc.file_name or "file"
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        await message.answer(
            f"Формат {extension or '(без расширения)'} пока не поддерживается.\n"
            f"Поддерживаемые форматы: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
        return

    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await message.answer("Файл слишком большой. Максимальный размер — 20 МБ.")
        return

    dest_dir = user_dir(message.from_user.id)
    dest_path = dest_dir / file_name

    # Скачиваем файл с серверов Telegram напрямую на диск
    await message.bot.download(doc, destination=dest_path)

    logger.info("Файл сохранён: %s (user_id=%s)", dest_path, message.from_user.id)

    await message.answer(f"Файл \"{file_name}\" получен. Извлекаю текст...")

    try:
        text = extract_text(dest_path)
    except ExtractionError as e:
        await message.answer(f"Не получилось обработать файл: {e}")
        return

    extracted_path = user_extracted_dir(message.from_user.id) / f"{Path(file_name).stem}.txt"
    extracted_path.write_text(text, encoding="utf-8")

    char_count = len(text)
    word_count = len(text.split())
    preview = text[:300].replace("\n", " ")

    await message.answer(
        f"Текст излвечен.\n\n"
        f"Количество символов: {char_count}\n"
        f"Количество слов: ~{word_count}\n\n"
        f"Начало текста:\n<i>{preview}…</i>\n\n"
        f"Зима близко."
    )


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_without_docs(message: Message) -> None:
    """
    Пока RAG не реализован — на любой обычный текст просто объясняем,
    что нужно сначала прислать файл.
    """
    await message.answer(
        "Пока я умею только принимать файлы. Пришли документ, чтобы я мог его сохранить — "
        "отвечать на вопросы по содержимому я научусь на следующих этапах."
    )