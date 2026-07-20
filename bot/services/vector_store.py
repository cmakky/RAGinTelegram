"""
Векторное хранилище chromadb. 

У каждого пользователя своя коллекция.
"""
import logging
import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.api.models.Collection import Collection

from bot.config import VECTOR_DB_DIR
from bot.services.chunking import Chunk

logger = logging.getLogger(__name__)

_client: chromadb.ClientAPI | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
    return _client


def get_user_collection(user_id: int) -> Collection:
    """
    Возвращает коллекцию пользователя.
    """
    client = _get_client()
    return client.get_or_create_collection(
        name=f"user_{user_id}",
        metadata={"hnsw:space": "cosine"}
    )


def add_chunks(
        user_id: int,
        file_name: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
) -> None:
    """
    Сохраняет чанки файла вместе с эмбеддингами в коллекцию пользователя.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("Кол-во чанков и эмбеддингов должны совпадать.")

    collection = get_user_collection(user_id)

    ids = [f"{file_name}::{c.index}" for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [
        {
            "file_name": file_name,
            "chunk_index": c.index,
            "char_start": c.char_start,
            "char_end": c.char_end,
        }
        for c in chunks
    ]

    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    logger.info("В коллекцию user_%s добавлено %d чанков из файла %s", user_id, len(chunks), file_name)


def query(user_id: int, query_embedding: list[float], top_k: int=5) -> dict:
    """
    Ищет топ_k чанков близких к query_embedding среди всех файлов пользователя.
    """
    collection = get_user_collection(user_id)
    return collection.query(query_embeddings=[query_embedding], n_results=top_k)


def list_files(user_id: str) -> dict[str, int]:
    """
    Возвращает {имя_файла: количество_чанок} каждого пользователя.
    """
    collection = get_user_collection(user_id)
    if collection.count() == 0:
        return {}
    
    result = collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for meta in result["metadatas"]:
        file_name = meta["file_name"]
        counts[file_name] = counts.get(file_name, 0) + 1
    return counts


def delete_file(user_id: int, file_name: str) -> int:
    """
    Удаляет все чанки файла из коллекции.
    
    Возвращает кол-во удаленных чанков.
    """
    collection = get_user_collection(user_id)
    existing = collection.get(where={"file_name": file_name}, include=[])
    ids = existing["ids"]
    if not ids:
        return 0

    collection.delete(where={"file_name": file_name})
    return len(ids)


def reset_user(user_id: int) -> None:
    """
    Полностью удаляет коллекцию пользователя.
    """
    client = _get_client()
    try:
        client.delete_collection(name=f"user_{user_id}")
    except Exception:
        pass
