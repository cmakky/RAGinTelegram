# RAGinTelegram

Реализован полный RAG-цикл. Добавлено управление данными пользователя:

- **`/help`** &mdash; список команд и краткое объяснение;
- **`/list`** &mdash; какие файлы загружены и сколько чанков у каждого;
- **`/delete имя_файла`** &mdash; удалить конкретный файл из индекса;
- **`/reset confirm`** &mdash; полностью очистить все данные пользователя.

**Оптимизация хранения:** оригинальные файлы в `storage/uploads/` по умолчанию удаляются сразу после успешного извлечения текста (`KEEP_UPLOADED_FILES = False` в конфиге).

## Структура проекта

```
telegram_rag_bot/
├── bot/
│   ├── main.py                     # точка входа, запуск polling
│   ├── config.py                   # переменные окружения, пути, константы
│   ├── handlers/
│   │   ├── start.py                # обработка /start
│   │   ├── files.py                # приём документов + весь пайплайн индексации
│   │   ├── questions.py            # поиск релевантных чанков + генерация ответа LLM
│   │   └── management.py           # /help, /list, /delete, /reset
│   └── services/
│       ├── text_extraction.py      # извлечение текста из pdf/docx/txt/md
│       ├── chunking.py             # разбиение текста на чанки с перекрытием
│       ├── embeddings.py           # эмбеддинги через intfloat/multilingual-e5-small
│       ├── vector_store.py         # обёртка над ChromaDB
│       └── llm.py                  # генерация ответа через Groq LLM на основе найденных чанков
├── storage/
│   ├── uploads/                    # файлы пользователей
│   ├── extracted/                  # извлечённый текст
│   ├── chunks/                     # нарезанные чанки в json
│   └── vectordb/                   # векторная база ChromaDB
├── .env.example
├── requirements.txt
└── README.md
```
