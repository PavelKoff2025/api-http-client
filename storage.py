import json
import time
from pathlib import Path

from api_client import CurrencyApiError, get_currency_rates

FAVORITE_CURRENCIES = ["USD", "EUR", "GBP", "RUB"]
DEFAULT_RATES_FILE = "currency_rate.json"
CACHE_MAX_AGE_HOURS = 24
MINI_CLI_TARGETS = ["RUB", "EUR", "GBP"]


class InvalidCurrencyCodeError(ValueError):
    """Код валюты отсутствует в списке доступных."""


def save_to_file(data: dict, path: str = DEFAULT_RATES_FILE) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_from_file(path: str = DEFAULT_RATES_FILE) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_cache_fresh(
    path: str = DEFAULT_RATES_FILE,
    max_age_hours: int = CACHE_MAX_AGE_HOURS,
) -> bool:
    file_path = Path(path)
    if not file_path.exists():
        return False
    age_seconds = time.time() - file_path.stat().st_mtime
    return age_seconds < max_age_hours * 3600


def file_exists(path: str = DEFAULT_RATES_FILE) -> bool:
    return Path(path).exists()


def get_conversion_rates(rates_data: dict) -> dict:
    """Словарь курсов. В API поле rates, в задании — conversion_rates."""
    return rates_data.get("rates", {})


def get_valid_currency_codes(rates_data: dict) -> set[str]:
    return set(get_conversion_rates(rates_data).keys())


def validate_currency_code(code: str, rates_data: dict) -> str:
    normalized = code.strip().upper()
    valid_codes = get_valid_currency_codes(rates_data)

    if normalized not in valid_codes:
        raise InvalidCurrencyCodeError(
            f"Код валюты «{normalized}» не найден в списке доступных. "
            f"Всего доступно кодов: {len(valid_codes)}. "
            f"Примеры: {', '.join(sorted(valid_codes)[:8])}"
        )

    return normalized


def get_reference_rates(path: str = DEFAULT_RATES_FILE) -> dict:
    if file_exists(path):
        try:
            all_data = read_from_file(path)
            if "USD" in all_data and all_data["USD"]:
                return all_data["USD"]
        except (json.JSONDecodeError, OSError):
            pass

    return get_currency_rates("USD")


def load_or_update_rates(
    base: str,
    path: str = DEFAULT_RATES_FILE,
) -> tuple[dict, str]:
    base = base.upper()
    all_data: dict = {}

    if file_exists(path):
        try:
            all_data = read_from_file(path)
        except (json.JSONDecodeError, OSError):
            all_data = {}

    if is_cache_fresh(path) and base in all_data and all_data[base]:
        return all_data[base], "файл"

    rates_data = get_currency_rates(base)
    all_data[base] = rates_data
    save_to_file(all_data, path)
    return rates_data, "API"


def update_all_currency_rates(path: str = DEFAULT_RATES_FILE) -> None:
    all_data = {}
    for currency in FAVORITE_CURRENCIES:
        all_data[currency] = get_currency_rates(currency)
    save_to_file(all_data, path)


def load_rates_data(path: str = DEFAULT_RATES_FILE) -> dict:
    return read_from_file(path)


def get_base_currencies(data: dict) -> list[str]:
    return [code for code in FAVORITE_CURRENCIES if code in data and data[code]]


def get_target_currencies(data: dict, base_currency: str) -> list[str]:
    entry = data.get(base_currency.upper())
    if not entry or not entry.get("rates"):
        return []
    return sorted(entry["rates"].keys())


def get_last_update(data: dict) -> str:
    for base in FAVORITE_CURRENCIES:
        entry = data.get(base)
        if entry and entry.get("time_last_update_utc"):
            return entry["time_last_update_utc"]
    return "—"


def convert_amount(
    from_currency: str,
    to_currency: str,
    amount: float,
    path: str = DEFAULT_RATES_FILE,
) -> tuple[float, float]:
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    rates_data, _ = load_or_update_rates(from_code, path)
    validate_currency_code(from_code, rates_data)
    validate_currency_code(to_code, rates_data)

    conversion_rates = get_conversion_rates(rates_data)
    rate = conversion_rates[to_code]
    result = round(amount * rate, 4)
    return result, rate


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    data: dict,
) -> tuple[float, float]:
    from_code = from_currency.upper()
    to_code = to_currency.upper()
    base_currencies = get_base_currencies(data)

    if from_code not in base_currencies:
        available = ", ".join(base_currencies)
        raise ValueError(
            f"«{from_code}» не является основной валютой. Доступны: {available}"
        )

    rates_data = data[from_code]
    validate_currency_code(from_code, rates_data)
    validate_currency_code(to_code, rates_data)

    conversion_rates = get_conversion_rates(rates_data)
    rate = conversion_rates[to_code]
    return amount * rate, rate
