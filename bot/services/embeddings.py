"""
Получение эмбеддингов для текста через локальную
модель intfloat/multilingual-e5-small.

Модель загружается при первом обращении к ней и
кэшируется в памяти процессора.
"""
import logging

from sentence_transformers import SentenceTransformer

from bot.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Загружается модель эмбеддингов.")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Модель эмбеддингов загружена.")
    return _model


def embed_passages(texts: list[str]) -> list[list[float]]:
    """
    Получает эмбеддинги для чанков, к-ые потом будут внесены в БД.
    """
    model = _get_model()
    prefixed = [f"passage: {t}" for t in texts]
    vectors = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """
    Получает эмбеддинг для запроса пользователя
    """
    model = _get_model()
    vector = model.encode([f"query: {text}"], normalize_embeddings=True, show_progress_bar=False)[0]
    return vector.tolist()