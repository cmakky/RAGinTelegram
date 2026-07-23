# RAGinTelegram

**RAGinTelegram** &mdash; это Telegram-бот, реализующий полный цикл **Retrieval-Augmented Generation (RAG)**: пользователь загружает файлы, бот извлекает из них текст, разбивает на чанки и отвечает на вопросы, опираясь только на релевантные фрагменты загруженных документов.

## Возможности

- **Загрузка документов** &mdash; поддержка PDF, DOCX, TXT и MD.
- **Поиск по документам** &mdash; эмбеддинги на базе `intfloat/multilingual-e5-small` и векторный поиск в ChromaDB.
- **Порог релевантности** &mdash; чанки с похожестью ниже `SIMILARITY_THRESHOLD` отсекаются до отправки в LLM, что экономит вызовы API и убирает нерелевантный контекст.
- **Память диалога** &mdash; бот помнит последние `MAX_HISTORY_EXCHANGES` сообщений и учитывает их при ответе.
- **Управление данными** &mdash; просмотр, удаление и полный сброс загруженных файлов и индекса.
- **Готов к деплою** &mdash; упакован в Docker.

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
│       ├── conversation.py         # память диалога
│       └── llm.py                  # генерация ответа через Groq LLM на основе найденных чанков
├── storage/
│   ├── uploads/                    # файлы пользователей
│   ├── extracted/                  # извлечённый текст
│   ├── chunks/                     # нарезанные чанки в json
│   └── vectordb/                   # векторная база ChromaDB
├── .env.example
├── Dockerfile                      # сборка образа бота
├── docker-compose.yml              # запуск
├── .dockerignore
├── requirements.txt
└── README.md
```

## Как запустить бота

### Локальный запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/cmakky/RAGinTelegram.git
   cd RAGinTelegram
   ```

2. Установите зависимости:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Создайте `.env` на основе примера и заполните переменные:

   ```bash
   cp .env.example .env
   ```

4. Запустите бота:

   ```bash
   python -m bot.main
   ```

### Запуск через Docker

1. Заполните `.env`.
2. Соберите и запустите контейнер:

   ```bash
   docker-compose up --build -d
   ```

Данные пользователей (`storage/`) сохраняются между перезапусками контейнера. Модель эмбеддингов скачивается на этапе сборки образа.

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Начало работы с ботом |
| `/help` | Список команд и краткое объяснение |
| `/list` | Какие файлы загружены  |
| `/delete имя_файла` | Удалить конкретный файл (без аргумента интерактивный список с кнопками) |
| `/reset confirm` | Полностью очистить все данные |

Просто отправьте документ (PDF / DOCX / TXT / MD), а затем задавайте вопросы по его содержимому в чате.

## Конфигурация

Переменные окружения задаются в файле `.env`:

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram-бота, полученный от [@BotFather](https://t.me/BotFather) |
| `GROQ_API_KEY` | Ключ для доступа к LLM API |

Дополнительные параметры настраиваются в `bot/config.py`:

- `KEEP_UPLOADED_FILES` &mdash; сохранять ли оригиналы файлов после извлечения текста (по умолчанию `False`).
- `SIMILARITY_THRESHOLD` &mdash; минимальный порог релевантности чанка для попадания в контекст LLM.
- `MAX_HISTORY_EXCHANGES` &mdash; сколько последних обменов сообщениями бот помнит в рамках диалога.

## Технологический стек

- **Python**;
- **[aiogram](https://docs.aiogram.dev/)**;
- **[ChromaDB](https://www.trychroma.com/)**;
- **[sentence-transformers](https://www.sbert.net/)** (`intfloat/multilingual-e5-small`);
- **[langchain-text-splitters](https://python.langchain.com/)**;
- **Docker**;