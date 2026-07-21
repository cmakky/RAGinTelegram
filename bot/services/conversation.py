"""
Хранение последних сообщений диалога для каждого пользователя.

Диалоги хранятся в памяти процессора. В дальнейшем можно улучшить
и подключить к этому всему БД.
"""
from collections import deque

from bot.config import MAX_HISTORY_EXCHANGES

_histories: dict[int, deque] = {}


def get_history(user_id: int) -> list[dict]:
    """
    Возвращает историю диалога пользователя (может быть пустой).
    """
    return list(_histories.get(user_id, []))


def add_exchange(user_id: int, question: str, answer: str) -> None:
    """
    Добавляет пару вопрос-ответ в историю, автоматически вытесняя старые.
    """
    if user_id not in _histories:
        _histories[user_id] = deque(maxlen=MAX_HISTORY_EXCHANGES * 2)
    _histories[user_id].append({"role": "user", "content": question})
    _histories[user_id].append({"role": "assistant", "content": answer})


def clear_history(user_id: int) -> None:
    """
    Полностью стирает историю диалога пользователя (вызывается из /reset).
    """
    _histories.pop(user_id, None)
