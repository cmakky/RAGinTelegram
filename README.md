# RAGinTelegram

## Структура проекта

```
RAGinTelegram/
├── bot/
│   ├── main.py                     # точка входа, запуск polling
│   ├── config.py                   # переменные окружения, пути, константы
│   ├── handlers/
│   │   ├── start.py                # обработка /start
│   │   └── files.py                # приём документов + извлечение текста + чанкинг
│   └── services/
│       ├── text_extraction.py      # извлечение текста из pdf/docx/txt/md
│       └── chunking.py             # разбиение текста на чанки с перекрытием
├── storage/
│   ├── uploads/                    # файлы, присланные пользователями
│   ├── extracted/                  # извлечённый текст
│   └── chunks/                     # нарезанные чанки в формате JSON
├── .env.example
├── requirements.txt
└── README.md
```
