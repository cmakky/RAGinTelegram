"""
Разбиение текста на чанки для поиска релевантных фрагментов в RAG-системе.

Используется реализация рекурсивной нарезки из библиотеки langchain-text-splitters.

Реализовано отслеживание точных позиций char_start и char_end
для отслеживания из какого места документа был взят ответ.
"""
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    index: int          # Порядковый номер чанка
    text: str           # Текст чанка
    char_start: int     # Позиция начала чанка
    char_end: int       # Позиция конца чанка


def chunk_text(text: str, chunk_size: int=1024, chunk_overlap=128) -> list[Chunk]:
    """
    Разбивает текст на чанки заданного размера с перекрытием.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    pieces = splitter.split_text(text)

    return _attach_positions(text, pieces)


def _attach_positions(text: str, pieces: list[str]) -> list[Chunk]:
    """
    Находит позицию каждого куска в исходном тексте.
    """
    chunks = []
    search_from = 0

    for i, piece in enumerate(pieces):
        start = text.find(piece, search_from)
        if start == -1:
            start = search_from
        end = start + search_from
        chunks.append(Chunk(index=i, text=piece, char_start=start, char_end=end))
        search_from = start + 1
    
    return chunks
    
