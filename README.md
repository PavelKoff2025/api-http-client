# HTTP-клиент — домашнее задание по работе с API

Консольное приложение на Python для тестовых HTTP-запросов к публичным API.  
Проект выполнен в рамках курса по работе с REST API.

## Возможности

### Задание 1 (минимум)

- GET-запросы к API вручную и через программу
- Получение ответа в формате JSON
- Извлечение ключевых полей из JSON (название, столица, население)
- Цветной вывод информации о стране

### Задание 2 (средний уровень)

- CLI-меню на русском языке
- HTTP-функции вынесены в отдельный модуль `http_client.py`
- Пункт меню «Случайная собака» (Dog CEO API)
- Запрос информации о стране (REST Countries API)

## Структура проекта

```
API/
├── main.py           # Главное CLI-меню
├── http_client.py    # HTTP-обёртка (get, проверка статуса)
├── country_info.py   # Красивый вывод данных о стране
├── homework.py       # Демонстрация задания 1
├── requirements.txt  # Зависимости
└── README.md
```

## Используемые API

| API | URL | Назначение |
|-----|-----|------------|
| REST Countries | `https://restcountries.com/v3.1/name/{country}` | Информация о странах |
| Dog CEO | `https://dog.ceo/api/breeds/image/random` | Случайное фото собаки |

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/PavelKoff2025/api-http-client.git
cd API

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Установить зависимости
pip install -r requirements.txt
```

## Запуск

### Главное меню

```bash
python main.py
```

```
1 — GET по URL
2 — Страна
3 — Случайная собака
0 — Выход
```

### Справочник стран (цветной вывод)

```bash
python country_info.py
```

### Демонстрация задания 1

```bash
python homework.py
```

## Примеры запросов

### Вручную (curl)

```bash
curl "https://restcountries.com/v3.1/name/russia"
curl "https://dog.ceo/api/breeds/image/random"
```

### Извлечение полей из JSON (Python)

```python
from http_client import get

response = get("https://restcountries.com/v3.1/name/russia")
country = response.json()[0]

print(country["name"]["common"])   # Russia
print(country["capital"][0])       # Moscow
print(country["population"])       # 146028325
```

## Зависимости

- [requests](https://pypi.org/project/requests/) — HTTP-запросы
- [colorama](https://pypi.org/project/colorama/) — цветной вывод в терминале

## Автор

Павел Кофф
