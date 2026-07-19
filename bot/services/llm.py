"""
Генерация ответа на запрос пользователя на основе найденных
чанков (RAG-система) через Groq API.
"""
import logging

from groq import AsyncGroq

from bot.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=GROQ_API_KEY)
    return _client


# Системный промпт. Здесь задается главное правило RAG
# для ответа на запросы пользователя.
SYSTEM_PROMPT = (
    "Ты — ассистент, отвечающий на вопросы пользователя строго на основе "
    "предоставленных фрагментов документа. Правила:\n"
    "1. Отвечай, используя ТОЛЬКО информацию из фрагментов ниже.\n"
    "2. Если ответа в фрагментах нет — прямо скажи, что не нашёл ответа "
    "в документе. Не додумывай и не используй свои общие знания.\n"
    "3. Отвечай на том же языке, на котором задан вопрос.\n"
    "4. Отвечай кратко и по существу, без лишней воды."
)


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[Фрагмент {i}, файл \"{chunk['file_name']}\"]\n{chunk['text']}")
    return "\n\n".join(parts)


async def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    chunks - список словарей, отсортированный по релевантности.
    """
    context = _build_context(chunks)
    user_message = f"Фрагмент документа:\n\n{context}\n\nВопрос: {question}"

    client = _get_client()
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    return response.choices[0].message.content