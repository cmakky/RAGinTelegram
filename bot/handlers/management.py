"""
Команды для управления загруженными документами:
/help, /list, /delete, /reset.
"""
import logging
import shutil
from pathlib import Path
 
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
 
from bot.config import UPLOADS_DIR, EXTRACTED_DIR, CHUNKS_DIR
from bot.services import vector_store
 
router = Router(name="management")
logger = logging.getLogger(__name__)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Я помогаю отвечать на вопросы по твоим документам (RAG-система).\n\n"
        "<b>Как пользоваться:</b>\n"
        "1. Пришли файл (PDF, DOCX, TXT или MD)\n"
        "2. Задавай вопросы - я найду релевантные фрагменты "
        "и отвечу на их основе\n\n"
        "<b>Команды:</b>\n"
        "/help - описание возможных функций;\n"
        "/list - список твоих загруженных файлов;\n"
        "/delete имя_файла - удалить конкретный файл;\n"
        "/reset confirm - удалить все файлы. Начать жизнь с чистого листа."
    )


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    files = vector_store.list_files(message.from_user.id)

    if not files:
        await message.answer(
            "У тебя нет загруженных файлов. Пришли что-нибудь, чтобы начать."
        )
        return

    lines = ["Твои загруженные файлы:\n"]
    for file_name, chunk_count in sorted(files.items()):
        lines.append(f"• {file_name} - {chunk_count} чанков")
    
    lines.append("\nЧтобы удалить файл: /delete имя_файла")
    await message.answer("\n".join(lines))


@router.message(Command("delete"))
async def cmd_delete(message: Message, command: CommandObject) -> None:
    file_name = (command.args or "").strip()
 
    if not file_name:
        await message.answer(
            "Укажи имя файла: /delete имя_файла\n"
            "Посмотреть точные имена можно через /list"
        )
        return
 
    user_id = message.from_user.id
    deleted_count = vector_store.delete_file(user_id, file_name)
 
    if deleted_count == 0:
        await message.answer(
            f"Файл \"{file_name}\" не найден. Проверь точное имя через /list "
            "(имя должно совпадать буква в букву)."
        )
        return
 
    # Очищаем кэш на диске после удаления файла.
    stem = Path(file_name).stem
    _unlink_if_exists(UPLOADS_DIR / str(user_id) / file_name)
    _unlink_if_exists(EXTRACTED_DIR / str(user_id) / f"{stem}.txt")
    _unlink_if_exists(CHUNKS_DIR / str(user_id) / f"{stem}.json")
 
    await message.answer(f"Файл «{file_name}» удален.")


@router.message(Command("reset"))
async def cmd_reset(message: Message, command: CommandObject) -> None:
    confirmed = (command.args or "").strip().lower() == "confirm"
 
    if not confirmed:
        await message.answer(
            "Это удалит ВСЕ твои загруженные файлы без возможности восстановить.\n\n"
            "Если уверен — напиши: /reset confirm"
        )
        return
 
    user_id = message.from_user.id
 
    vector_store.reset_user(user_id)
    shutil.rmtree(UPLOADS_DIR / str(user_id), ignore_errors=True)
    shutil.rmtree(EXTRACTED_DIR / str(user_id), ignore_errors=True)
    shutil.rmtree(CHUNKS_DIR / str(user_id), ignore_errors=True)
 
    logger.info("Полный сброс данных пользователя user_id=%s", user_id)
    await message.answer("Жизнь с чистого листа.")


def _unlink_if_exists(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass
