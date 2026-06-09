from colorama import Fore, Style, init
from http_client import HttpError, get

init(autoreset=True)

API_URL = "https://restcountries.com/v3.1/name/{country}"


def fetch_country(country: str) -> dict | None:
    try:
        response = get(API_URL.format(country=country), timeout=30)
    except HttpError as error:
        if "404" in str(error):
            print(f"{Fore.RED}Страна «{country}» не найдена.")
        else:
            print(f"{Fore.RED}{error}")
        return None

    data = response.json()
    return data[0] if isinstance(data, list) and data else None


def _format_number(value: int | float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def _join_list(items: list | None) -> str:
    return ", ".join(items) if items else "—"


def _print_field(label: str, value: str, value_color: str = Fore.YELLOW) -> None:
    print(f"{Fore.CYAN}{Style.BRIGHT}{label}:{Style.RESET_ALL}")
    print(f"  {value_color}{value}{Style.RESET_ALL}")
    print()


def _print_link(label: str, url: str) -> None:
    print(f"{Fore.CYAN}{Style.BRIGHT}{label}:{Style.RESET_ALL}")
    if url and url != "—":
        print(f"  {Fore.BLUE}{Style.BRIGHT}{url}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}—{Style.RESET_ALL}")
    print()


def print_country_info(country_data: dict) -> None:
    name = country_data.get("name", {})
    common = name.get("common", "—")
    official = name.get("official", "—")
    flag = country_data.get("flag", "")

    translations = country_data.get("translations", {})
    russian = translations.get("rus", {})
    name_ru = russian.get("common", "—")

    capital = _join_list(country_data.get("capital"))
    region = country_data.get("region", "—")
    subregion = country_data.get("subregion", "—")
    population = _format_number(country_data.get("population", 0))
    area = _format_number(country_data.get("area", 0))
    borders = _join_list(country_data.get("borders"))
    timezones = _join_list(country_data.get("timezones"))
    continents = _join_list(country_data.get("continents"))

    languages = country_data.get("languages", {})
    languages_str = ", ".join(languages.values()) if languages else "—"

    currencies = country_data.get("currencies", {})
    currency_parts = []
    for code, info in currencies.items():
        symbol = info.get("symbol", "")
        currency_name = info.get("name", "")
        currency_parts.append(f"{code} ({symbol}) — {currency_name}")
    currencies_str = "; ".join(currency_parts) if currency_parts else "—"

    latlng = country_data.get("latlng", [])
    coordinates = f"{latlng[0]}°, {latlng[1]}°" if len(latlng) == 2 else "—"

    flags = country_data.get("flags", {})
    flag_png = flags.get("png", "—")
    flag_svg = flags.get("svg", "—")

    maps = country_data.get("maps", {})
    google_maps = maps.get("googleMaps", "—")
    open_street_maps = maps.get("openStreetMaps", "—")

    print()
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'═' * 50}")
    print(f"  {Fore.RED}{Style.BRIGHT}{flag}{Style.RESET_ALL}  {Fore.MAGENTA}{Style.BRIGHT}{common}{Style.RESET_ALL}")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    print()

    _print_field("Флаг", flag, Fore.RED + Style.BRIGHT)
    _print_link("Флаг (PNG)", flag_png)
    _print_link("Флаг (SVG)", flag_svg)

    fields = [
        ("Официальное название", official),
        ("Название на русском", name_ru),
        ("Столица", capital),
        ("Регион", region),
        ("Подрегион", subregion),
        ("Континент", continents),
        ("Население", population),
        ("Площадь (км²)", area),
        ("Языки", languages_str),
        ("Валюта", currencies_str),
        ("Границы (коды)", borders),
        ("Часовые пояса", timezones),
        ("Координаты", coordinates),
    ]

    for label, value in fields:
        _print_field(label, value)

    _print_link("Google Maps", google_maps)
    _print_link("OpenStreetMap", open_street_maps)


def main() -> None:
    print(f"{Fore.GREEN}{Style.BRIGHT}=== Справочник стран ==={Style.RESET_ALL}\n")

    while True:
        country = input(f"{Fore.CYAN}Введите страну (Enter — выход): {Style.RESET_ALL}").strip()

        if not country:
            print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
            break

        country_data = fetch_country(country)
        if country_data:
            print_country_info(country_data)

        print(f"{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
