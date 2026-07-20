from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Валар моргулис! Я помогу отвечать на вопросы по твоим документам.\n\n"
        "Пришли мне файл (PDF, DOCX, TXT или MD), а затем задавай вопросы по его содержимому.\n\n"
        "Все возможности доступны по команде /help"
    )