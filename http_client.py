import requests


class HttpError(Exception):
    """Ошибка HTTP-запроса."""


def get(url: str, params: dict | None = None, timeout: int = 10) -> requests.Response:
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as error:
        raise HttpError(f"Не удалось выполнить запрос: {error}") from error

    if not response.ok:
        raise HttpError(f"Ошибка HTTP {response.status_code}: {response.reason}")

    return response
