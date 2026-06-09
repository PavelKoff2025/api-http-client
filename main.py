import json

from colorama import Fore, Style, init
from http_client import HttpError, get

from country_info import fetch_country, print_country_info

init(autoreset=True)

DOG_API_URL = "https://dog.ceo/api/breeds/image/random"


def show_get_by_url() -> None:
    url = input(f"{Fore.CYAN}Введите URL: {Style.RESET_ALL}").strip()
    if not url:
        print(f"{Fore.YELLOW}URL не указан.{Style.RESET_ALL}")
        return

    try:
        response = get(url)
        print(f"\n{Fore.GREEN}Статус: {response.status_code}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Ответ (JSON):{Style.RESET_ALL}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except HttpError as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.CYAN}Ответ (текст):{Style.RESET_ALL}")
        print(response.text)


def show_country() -> None:
    country = input(f"{Fore.CYAN}Введите страну: {Style.RESET_ALL}").strip()
    if not country:
        print(f"{Fore.YELLOW}Название страны не указано.{Style.RESET_ALL}")
        return

    country_data = fetch_country(country)
    if country_data:
        print_country_info(country_data)


def show_random_dog() -> None:
    try:
        response = get(DOG_API_URL)
        data = response.json()
        image_url = data.get("message", "—")
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Случайная собака 🐶{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Ссылка на изображение:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{image_url}{Style.RESET_ALL}")
    except HttpError as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
    except (ValueError, KeyError) as error:
        print(f"{Fore.RED}Не удалось разобрать ответ API: {error}{Style.RESET_ALL}")


def main() -> None:
    print(f"{Fore.GREEN}{Style.BRIGHT}=== HTTP-клиент ==={Style.RESET_ALL}\n")

    while True:
        print(f"{Fore.MAGENTA}1{Style.RESET_ALL} — GET по URL")
        print(f"{Fore.MAGENTA}2{Style.RESET_ALL} — Страна")
        print(f"{Fore.MAGENTA}3{Style.RESET_ALL} — Случайная собака")
        print(f"{Fore.MAGENTA}0{Style.RESET_ALL} — Выход")

        choice = input(f"\n{Fore.CYAN}Выберите пункт меню (0–3): {Style.RESET_ALL}").strip()

        if choice == "0":
            print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
            break
        elif choice == "1":
            show_get_by_url()
        elif choice == "2":
            show_country()
        elif choice == "3":
            show_random_dog()
        else:
            print(f"{Fore.RED}Неверный выбор. Попробуйте снова.{Style.RESET_ALL}")

        print(f"\n{Fore.MAGENTA}{'─' * 40}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
