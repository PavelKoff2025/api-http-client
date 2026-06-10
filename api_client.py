import requests

API_BASE_URL = "https://open.er-api.com/v6/latest/{base}"
REQUEST_TIMEOUT = 10


class CurrencyApiError(Exception):
    """Ошибка при запросе курсов валют."""


def get_currency_rates(base: str) -> dict:
    url = API_BASE_URL.format(base=base.upper())

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as error:
        raise CurrencyApiError(
            f"Не удалось выполнить запрос курсов для «{base}»: {error}"
        ) from error

    if response.status_code != 200:
        raise CurrencyApiError(
            f"Ошибка API для «{base}»: сервер вернул код {response.status_code}"
        )

    return response.json()
