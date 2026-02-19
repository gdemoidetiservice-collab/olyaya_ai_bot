# 🔥 Оля-ля — Дерзкая ИИ-ассистентка

Telegram-бот с характером. Психолог, коуч, лучшая подруга-стерва.  
Работает на Google Gemini (бесплатно). Хостинг на Railway.

---

## ⚡ Быстрый старт

### Шаг 1 — Создай бота в Telegram

1. Открой [@BotFather](https://t.me/BotFather)
2. Отправь `/newbot`
3. Придумай имя и username (должен заканчиваться на `bot`)
4. Скопируй **BOT_TOKEN**

### Шаг 2 — Получи Gemini API ключ

1. Открой [aistudio.google.com](https://aistudio.google.com)
2. Войди через Google аккаунт
3. Нажми **Get API Key** → **Create API Key**
4. Скопируй **GEMINI_API_KEY**

### Шаг 3 — Узнай свой Telegram ID

Напиши [@userinfobot](https://t.me/userinfobot) — он пришлёт твой ID.

### Шаг 4 — Загрузи на GitHub

1. Создай новый репозиторий на GitHub (публичный или приватный)
2. Загрузи все файлы из этой папки
3. **Не загружай .env** — он в .gitignore

### Шаг 5 — Задеплой на Railway

1. Открой [railway.app](https://railway.app)
2. Войди через GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Выбери свой репозиторий
5. Перейди в **Variables** и добавь:

```
BOT_TOKEN=твой_токен_от_BotFather
GEMINI_API_KEY=твой_ключ_Gemini
OWNER_ID=твой_telegram_id
PASSWORD=salampopolam
```

6. Railway автоматически запустит бота

---

## 💬 Как общаться с ботом

Всё через обычный текст — кнопок нет.

| Что написать | Что сделает |
|---|---|
| Просто текст | Ответит как психолог/подруга |
| `/знакомство` | Запустит опросник из 20 вопросов |
| `запиши тренировку завтра 18:00` | Создаст задачу и .ics для iPhone |
| `мои задачи` | Покажет список задач |
| `/отчет` | Пришлёт Excel файл |
| `погода` | Погода в Костроме |

---

## 📅 Автоматические сообщения

- **07:00** — утреннее приветствие с погодой и задачами
- **22:00** — вечерний разбор дня
- **3-10 раз в день** — случайные пинки и вопросы

---

## 🔐 Доступ

- **Владелец** (OWNER_ID) — полный доступ без пароля
- **Другие** — нужен пароль из переменной PASSWORD

---

## 🗂 Структура файлов

```
olyaya_bot/
├── bot.py              # Главный файл — запуск бота
├── ai.py               # Интеграция с Gemini
├── config.py           # Конфигурация
├── prompts.py          # Личность и вопросы
├── memory.py           # Память пользователя
├── scheduler.py        # Планировщик сообщений
├── weather.py          # Погода (Open-Meteo, бесплатно)
├── calendar_utils.py   # Создание .ics файлов
├── excel_utils.py      # Excel отчёты
├── requirements.txt    # Зависимости Python
├── Dockerfile          # Docker образ
├── .env.example        # Пример переменных
├── .gitignore
└── .github/
    └── workflows/
        └── ci.yml      # GitHub Actions
```

---

## 🐛 Частые ошибки

**TelegramConflictError** — бот запущен в двух местах одновременно.  
→ Останови все локальные запуски, оставь только Railway.

**GEMINI_API_KEY not set** — не добавил переменную в Railway Variables.

**BOT_TOKEN not set** — то же самое.
