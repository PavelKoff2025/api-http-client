"""
Домашнее задание 1 (минимум):
- запросы к API стран (вручную через curl/браузер и через программу);
- ответ в формате JSON;
- извлечение 2–3 ключевых полей из ответа.
"""

import json

import requests
from colorama import Fore, Style, init

init(autoreset=True)

API_URL = "https://restcountries.com/v3.1/name/{country}"


def get_country_json(country: str) -> list | None:
    """GET-запрос к API. Возвращает JSON-ответ (список стран)."""
    response = requests.get(API_URL.format(country=country), timeout=30)
    response.raise_for_status()
    return response.json()


def extract_key_fields(country_data: dict) -> dict:
    """
    Извлекаем 2–3 ключевых поля из JSON, как в country_info.
    Аналог примера с main_temp: берём нужное поле и выводим значение.
    """
    name = country_data.get("name", {})
    capital = country_data.get("capital", [])
    population = country_data.get("population")

    return {
        "name": name.get("common"),
        "capital": capital[0] if capital else None,
        "population": population,
    }


def print_country_summary(country: str) -> None:
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'=' * 40}")
    print(f"Страна: {country}")
    print(f"{'=' * 40}{Style.RESET_ALL}")

    try:
        data = get_country_json(country)
    except requests.RequestException as error:
        print(f"{Fore.RED}Ошибка: {error}")
        return

    print(f"\n{Fore.CYAN}Тип ответа:{Style.RESET_ALL} JSON (список объектов)")
    print(f"{Fore.CYAN}Количество результатов:{Style.RESET_ALL} {len(data)}")

    country_data = data[0]
    fields = extract_key_fields(country_data)

    print(f"\n{Fore.GREEN}{Style.BRIGHT}Ключевые поля из JSON:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}name (название):{Style.RESET_ALL}     {Fore.YELLOW}{fields['name']}{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}capital (столица):{Style.RESET_ALL}  {Fore.YELLOW}{fields['capital']}{Style.RESET_ALL}")
    print(
        f"  {Fore.CYAN}population (население):{Style.RESET_ALL} "
        f"{Fore.YELLOW}{fields['population']:,}{Style.RESET_ALL}".replace(",", " ")
    )


def demo_requests() -> None:
    """Несколько простых запросов через программу."""
    countries = ["russia", "germany", "japan"]

    print(f"{Fore.GREEN}{Style.BRIGHT}=== Домашнее задание: запросы по странам ==={Style.RESET_ALL}")
    print("\nПримеры ручных запросов (curl):")
    for country in countries:
        print(f"  curl \"{API_URL.format(country=country)}\"")

    for country in countries:
        print_country_summary(country)

    print(f"\n{Fore.MAGENTA}{'─' * 40}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Готово: получили JSON и извлекли name, capital, population.{Style.RESET_ALL}\n")


if __name__ == "__main__":
    demo_requests()
