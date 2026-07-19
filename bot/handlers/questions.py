"""
Обработка вопросов пользователя, поиск релевантных чанков по векторной базе.
"""
import asyncio
import logging

from aiogram import Router, F
from aiogram.types import Message
from groq import GroqError

from bot.config import TOP_K_RESULTS
from bot.services.embeddings import embed_query
from bot.services import vector_store
from bot.services import llm

router = Router(name="questions")
logger = logging.getLogger(__name__)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_question(message: Message) -> None:
    question = message.text
    user_id = message.from_user.id

    collection = vector_store.get_user_collection(user_id)
    if collection.count() == 0:
        await message.answer(
            "У тебя пока нет загруженных документов. Пришли файлы," \
            "а потом можно будет задавать вопросы."
        )
        return
    
    await message.answer("Ищу релевантные фрагменты...")

    query_embedding = await asyncio.to_thread(embed_query, question)
    results = await asyncio.to_thread(vector_store.query, user_id, query_embedding, TOP_K_RESULTS)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        await message.answer("Не нашел ничего подходящего в твоих документах.")
        return

    chunks = [
        {"text": doc, "file_name": meta["file_name"]}
        for doc, meta in zip(documents, metadatas)
    ]

    try:
        answer = await llm.generate_answer(question, chunks)
    except GroqError as e:
        logger.error("Ошибка при обращении к Groq API: %s", e)
        await message.answer(
            "Не удалось получить ответ от LLM (проблема с API)."
        )
        return
    
    source_files = sorted({meta["file_name"] for meta in metadatas})
    sources_line = ", ".join(source_files)

    await message.answer(f"{answer}\n\n<i>Источник: {sources_line}</i>")
