# Домашнее задание — валюты. Задание 1 (база)

**API:** [open.er-api.com](https://open.er-api.com)  
**Документация:** [exchangerate-api.com/docs/free](https://www.exchangerate-api.com/docs/free)  
**Эндпоинт:** `GET https://open.er-api.com/v6/latest/{BASE_CODE}`

## 5 ключевых полей ответа `latest`

| № | Поле | Тип | Описание | Пример значения |
|---|------|-----|----------|-----------------|
| 1 | `result` | string | Статус запроса: `success` при успехе, `error` при ошибке | `"success"` |
| 2 | `base_code` | string | Базовая валюта (ISO 4217), относительно которой даны все курсы | `"USD"` |
| 3 | `time_last_update_utc` | string | Дата и время последнего обновления курсов (UTC) | `"Wed, 10 Jun 2026 00:02:31 +0000"` |
| 4 | `time_next_update_utc` | string | Дата и время следующего обновления курсов (UTC) | `"Thu, 11 Jun 2026 00:29:01 +0000"` |
| 5 | `rates` | object | Словарь курсов: сколько единиц каждой валюты за 1 единицу `base_code` | `rates.RUB` → `72.02998`, `rates.USD` → `1` |

## Примечание

В задании в примере указано `conversion_rates`, но в документации **open.er-api.com** поле называется **`rates`**, не `conversion_rates`.

## Пример фрагмента ответа

```json
{
  "result": "success",
  "base_code": "USD",
  "time_last_update_utc": "Wed, 10 Jun 2026 00:02:31 +0000",
  "time_next_update_utc": "Thu, 11 Jun 2026 00:29:01 +0000",
  "rates": {
    "USD": 1,
    "EUR": 0.865865,
    "RUB": 72.02998
  }
}
```

## Дополнительные полезные поля (из документации)

- `time_last_update_unix` — время последнего обновления (Unix timestamp)
- `time_next_update_unix` — время следующего обновления (Unix timestamp)
- `time_eol_unix` — ожидаемое время отключения эндпоинта (0 = не запланировано)
- `provider` — источник данных
- `error-type` — тип ошибки (только при `result: "error"`)
