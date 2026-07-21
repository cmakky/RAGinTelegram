"""
Команды для управления загруженными документами:
/help, /list, /delete, /reset.
"""
import logging
import shutil
from pathlib import Path
 
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import UPLOADS_DIR, EXTRACTED_DIR, CHUNKS_DIR
from bot.services import vector_store
from bot.services import conversation
 
router = Router(name="management")
logger = logging.getLogger(__name__)

PAGE_SIZE = 5 # Сколько файлов показывать на одной странице

_delete_sessions: dict[int, list[str]] = {}


class DeleteCB(CallbackData, prefix="del"):
    action: str
    value: int


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
        "/delete - выбрать файл для удаления;\n"
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
 
    # Способ 1: /delete имя_файла - прямое удаление без кнопок
    if file_name:
        await _delete_and_reply(message.from_user.id, file_name, message.answer)
        return
 
    # Способ 2: /delete без аргументов - показываем кнопки
    user_id = message.from_user.id
    files = sorted(vector_store.list_files(user_id).keys())
 
    if not files:
        await message.answer("У тебя пока нет загруженных файлов.")
        return
 
    _delete_sessions[user_id] = files
    text, keyboard = _build_file_list_view(files, page=0)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(DeleteCB.filter(F.action == "page"))
async def on_delete_page(query: CallbackQuery, callback_data: DeleteCB) -> None:
    user_id = query.from_user.id
    files = _delete_sessions.get(user_id)
 
    if files is None:
        await query.answer("Вызови /delete заново", show_alert=True)
        return
 
    text, keyboard = _build_file_list_view(files, page=callback_data.value)
    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()
 
 
@router.callback_query(DeleteCB.filter(F.action == "pick"))
async def on_delete_pick(query: CallbackQuery, callback_data: DeleteCB) -> None:
    user_id = query.from_user.id
    files = _delete_sessions.get(user_id)
 
    if files is None or callback_data.value >= len(files):
        await query.answer("Вызови /delete заново", show_alert=True)
        return
 
    file_name = files[callback_data.value]
 
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, удалить", callback_data=DeleteCB(action="confirm", value=callback_data.value))
    builder.button(text="Отмена", callback_data=DeleteCB(action="cancel", value=0))
    builder.adjust(2)
 
    await query.message.edit_text(
        f"Удалить файл <code>{file_name}</code>?\nЭто действие нельзя отменить.",
        reply_markup=builder.as_markup(),
    )
    await query.answer()
 
 
@router.callback_query(DeleteCB.filter(F.action == "confirm"))
async def on_delete_confirm(query: CallbackQuery, callback_data: DeleteCB) -> None:
    user_id = query.from_user.id
    files = _delete_sessions.get(user_id)
 
    if files is None or callback_data.value >= len(files):
        await query.answer("Вызови /delete заново", show_alert=True)
        return
 
    file_name = files[callback_data.value]
 
    async def reply(text: str) -> None:
        await query.message.edit_text(text)
 
    await _delete_and_reply(user_id, file_name, reply)
    _delete_sessions.pop(user_id, None)
    await query.answer()
 
 
@router.callback_query(DeleteCB.filter(F.action == "cancel"))
async def on_delete_cancel(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    _delete_sessions.pop(user_id, None)
    await query.message.edit_text("Отменено.")
    await query.answer()


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
    conversation.clear_history(user_id)
    _delete_sessions.pop(user_id, None)
    shutil.rmtree(UPLOADS_DIR / str(user_id), ignore_errors=True)
    shutil.rmtree(EXTRACTED_DIR / str(user_id), ignore_errors=True)
    shutil.rmtree(CHUNKS_DIR / str(user_id), ignore_errors=True)
 
    logger.info("Полный сброс данных пользователя user_id=%s", user_id)
    await message.answer("Все удалено. Жизнь с чистого листа.")


async def _delete_and_reply(user_id: int, file_name: str, reply) -> None:
    """
    Общая логика удаления файла. 
    
    Используется и из /delete имя_файла, и из кнопок.
    """
    deleted_count = vector_store.delete_file(user_id, file_name)
 
    if deleted_count == 0:
        await reply(
            f"Файл «{file_name}» не найден. Проверь точное имя через /list "
            "(имя должно совпадать буква в букву)."
        )
        return
 
    stem = Path(file_name).stem
    _unlink_if_exists(UPLOADS_DIR / str(user_id) / file_name)
    _unlink_if_exists(EXTRACTED_DIR / str(user_id) / f"{stem}.txt")
    _unlink_if_exists(CHUNKS_DIR / str(user_id) / f"{stem}.json")
 
    await reply(f"Файл «{file_name}» удален.")
 
 
def _build_file_list_view(files: list[str], page: int) -> tuple[str, InlineKeyboardMarkup]:
    """
    Строит интерфейс для одной страницы списка файлов.
    """
    total_pages = (len(files) - 1) // PAGE_SIZE + 1
    page = max(0, min(page, total_pages - 1))
 
    start = page * PAGE_SIZE
    page_files = files[start:start + PAGE_SIZE]
 
    builder = InlineKeyboardBuilder()
    for i, file_name in enumerate(page_files, start=start): 
        label = file_name if len(file_name) <= 40 else file_name[:37] + "…"
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=DeleteCB(action="pick", value=i).pack(),
            )
        )
 
    nav_row = []
    if page > 0:
        nav_row.append(("Назад", DeleteCB(action="page", value=page - 1)))
    if page < total_pages - 1:
        nav_row.append(("Вперед", DeleteCB(action="page", value=page + 1)))
    if nav_row:
        builder.row(*[
            InlineKeyboardButton(text=t, callback_data=cb.pack())
            for t, cb in nav_row
        ])
 
    text = f"Выбери файл для удаления (страница {page + 1} из {total_pages}):"
    return text, builder.as_markup()
 
 
def _unlink_if_exists(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass
