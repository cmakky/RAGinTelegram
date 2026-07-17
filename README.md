# RAGinTelegram

## Структура проекта

```
RAGinTelegram/
├── bot/
│   ├── main.py                     # точка входа, запуск polling
│   ├── config.py                   # переменные окружения, пути, константы
│   ├── handlers/
│   │   ├── start.py                # обработка /start
│   │   └── files.py                # приём документов + запуск извлечения текста
│   └── services/
│       └── text_extraction.py      # извлечение текста из pdf/docx/txt/md
├── storage/
│   ├── uploads/                    # сюда сохраняются файлы, присланные пользователями
│   └── extracted/                  # сюда сохраняется извлеченный из файлов текст
├── .env                            # токен бота
├── .gitignore
├── requirements.txt
└── README.md
```
