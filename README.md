# FinPi Web Scraper

Веб-скрапер для парсинга товаров с различных интернет-магазинов с использованием ScraperAPI.

## Описание

Этот проект представляет собой универсальный веб-скрапер, который может парсить товары с различных сайтов:
- **Rozetka** (Украина) - интернет-магазин электроники и товаров для дома
- **Tesco** (Великобритания) - продуктовый супермаркет
- **Rost** (Украина) - продуктовый магазин
и другие

## Возможности

- ✅ Универсальная конфигурация через JSON
- ✅ Поддержка JavaScript-рендеринга для динамических сайтов
- ✅ Автоматическая прокрутка страниц
- ✅ **Автоматическая пагинация** - листание страниц для сбора большего количества товаров
- ✅ **Контроль количества** - указывайте сколько товаров собрать (10, 110, 1010)
- ✅ **Иерархия папок** - автоматическое создание структуры GOODS/GROCERIES/BEVERAGES
- ✅ **Динамические имена файлов** - rozetka_whisky.txt, tesco_whisky.txt
- ✅ Сохранение результатов в отдельные файлы
- ✅ Обработка ошибок и логирование
- ✅ Использование ScraperAPI для обхода блокировок

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd finpi-scraper
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте ваш API ключ ScraperAPI:
```
SCRAPERAPI_KEY=ваш_api_ключ_здесь
```

## Использование

1. Настройте сайты в файле `config.json`
2. Запустите скрипт:
```bash
python main.py
```

Результаты будут сохранены в иерархической структуре папок:
```
output/
├── GOODS/
│   └── GROCERIES/
│       └── BEVERAGES/
│           ├── rozetka_whisky.txt
│           └── tesco_whisky.txt
```

## Конфигурация

Файл `config.json` содержит настройки для каждого сайта:

```json
[
  {
    "site_name": "rozetka",
    "category_name": "whisky",
    "url": "https://rozetka.com.ua/ua/viski/c4649130/",
    "category_path": "GOODS/GROCERIES/BEVERAGES",
    "target_count": 1010,
    "product_name_selector": ".tile-title",
    "pagination_template": "/page={page}/",
    "needs_scrolling": true,
    "js_rendering": true
  }
]
```

### Параметры конфигурации:
- `site_name` - название сайта (для имени файла)
- `category_name` - название категории (для имени файла)
- `url` - URL страницы для парсинга
- `category_path` - путь для создания папок (GOODS/GROCERIES/BEVERAGES)
- `target_count` - количество товаров для сбора
- `product_name_selector` - CSS селектор для названий товаров
- `pagination_template` - шаблон для пагинации (/page={page}/ или ?page={page})
- `needs_scrolling` - нужна ли прокрутка страницы
- `js_rendering` - нужен ли рендеринг JavaScript

## Структура проекта

```
finpi_scraper/
├── main.py              # Основной скрипт
├── config.json          # Конфигурация сайтов
├── requirements.txt     # Python зависимости
├── .env                 # Переменные окружения (не в git)
├── output/              # Результаты парсинга
└── README.md           # Документация
```

## Требования

- Python 3.7+
- ScraperAPI аккаунт и API ключ
- Интернет соединение

## Зависимости

- `beautifulsoup4` - для парсинга HTML
- `requests` - для HTTP запросов
- `python-dotenv` - для работы с переменными окружения

## Лицензия

Этот проект создан для образовательных целей.
