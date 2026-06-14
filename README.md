# HTTP-клиент — домашнее задание по работе с API

Консольное приложение на Python для тестовых HTTP-запросов к публичным API.  
Проект выполнен в рамках курса по работе с REST API.

**Репозиторий:** https://github.com/PavelKoff2025/api-http-client

## Возможности

### Модуль стран и HTTP-клиент

- GET-запросы к API вручную и через программу
- Получение ответа в формате JSON
- Извлечение ключевых полей из JSON (название, столица, население)
- Цветной вывод информации о стране
- CLI-меню на русском языке
- HTTP-функции в модуле `http_client.py`
- Пункт меню «Случайная собака» (Dog CEO API)

### Модуль валют (open.er-api.com)

- Запрос курсов валют и кэширование в `currency_rate.json`
- Мини-CLI: базовая валюта → курсы RUB, EUR, GBP
- Конвертер суммы с точностью 4 знака
- Валидация кодов валют по `rates.keys()`
- Разделение на модули: `api_client.py`, `storage.py`, `cli.py`

### Модуль погоды (OpenWeatherMap)

- Geocoding API и Current Weather API
- CLI: запрос по городу или координатам
- Кэширование последнего ответа в `weather_cache.json` (до 3 часов)
- Повторы при 429 и сетевых ошибках (1s, 2s, 4s)
- Ключ API хранится в `.env`

## Структура проекта

```
API/
├── main.py              # CLI: страны, собаки, GET-запросы
├── http_client.py       # HTTP-обёртка (задание по странам)
├── country_info.py      # Цветной вывод данных о стране
├── homework.py          # Демонстрация задания 1 (страны)
├── api_client.py        # HTTP-запросы к API валют
├── storage.py           # Кэш, I/O, конвертация, валидация
├── cli.py               # CLI конвертера валют
├── currency.py          # Точка входа конвертера валют
├── test_acceptance.py   # Проверка критериев приёмки
├── homework_currency.md # Документация ДЗ по валютам (задание 1)
├── weather_app.py       # CLI погоды (OpenWeatherMap)
├── requirements.txt
└── README.md
```

## Используемые API

| API | URL | Назначение |
|-----|-----|------------|
| REST Countries | `https://restcountries.com/v3.1/name/{country}` | Информация о странах |
| Dog CEO | `https://dog.ceo/api/breeds/image/random` | Случайное фото собаки |
| Exchange Rate API | `https://open.er-api.com/v6/latest/{base}` | Курсы валют |
| OpenWeatherMap | `https://api.openweathermap.org` | Геокодинг и текущая погода |

## Установка

```bash
git clone https://github.com/PavelKoff2025/api-http-client.git
cd api-http-client

python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

Создайте файл `.env` с ключом OpenWeather:

```bash
API_KEY=ваш_ключ
```

## Запуск

### HTTP-клиент (страны, собаки)

```bash
python main.py
```

### Конвертер валют

```bash
python cli.py
# или
python currency.py
```

### Проверка критериев приёмки

```bash
python test_acceptance.py
```

### Справочник стран

```bash
python country_info.py
```

### Погода

```bash
python weather_app.py
```

## Критерии приёмки (валюты)

- Запуск в чистом venv с `requests` и `colorama`
- Корректное создание/чтение `currency_rate.json`
- Конвертация USD→RUB и EUR→GBP одинакова для кэша и свежего API-ответа
- Ошибки (невалидная валюта, сеть) выводятся пользователю без stack trace

## Зависимости

- [requests](https://pypi.org/project/requests/) — HTTP-запросы
- [colorama](https://pypi.org/project/colorama/) — цветной вывод в терминале
- [python-dotenv](https://pypi.org/project/python-dotenv/) — загрузка переменных из `.env`

## Автор

Павел Кофф
