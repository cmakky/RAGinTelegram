# RAGinTelegram

## Структура проекта


```
telegram_rag_bot/
├── bot/
│   ├── main.py                     # точка входа, запуск polling
│   ├── config.py                   # переменные окружения, пути, константы
│   ├── handlers/
│   │   ├── start.py                # обработка /start
│   │   └── files.py                # приём документов + весь пайплайн индексации
│   └── services/
│       ├── text_extraction.py      # извлечение текста из pdf/docx/txt/md
│       ├── chunking.py             # разбиение текста на чанки с перекрытием
│       ├── embeddings.py           # эмбеддинги через intfloat/multilingual-e5-small
│       └── vector_store.py         # обертка над chromabd
├── storage/
│   ├── uploads/                    # файлы пользователей
│   ├── extracted/                  # извлечённый текст
│   ├── chunks/                     # нарезанные чанки в json
│   └── vectordb/                   # векторная база chromabd
├── .env.example
├── requirements.txt
└── README.md
```
