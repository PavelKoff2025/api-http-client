import json

from colorama import Fore, Style, init

from api_client import CurrencyApiError
from storage import (
    DEFAULT_RATES_FILE,
    MINI_CLI_TARGETS,
    InvalidCurrencyCodeError,
    convert_amount,
    convert_currency,
    file_exists,
    get_base_currencies,
    get_conversion_rates,
    get_last_update,
    get_reference_rates,
    get_target_currencies,
    load_or_update_rates,
    load_rates_data,
    update_all_currency_rates,
    validate_currency_code,
)

init(autoreset=True)


def print_mini_cli_rates(base: str, rates_data: dict, source: str) -> None:
    rates = get_conversion_rates(rates_data)
    updated = rates_data.get("time_last_update_utc", "—")

    print(f"\n{Fore.GREEN}{Style.BRIGHT}Курсы для базы {base}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Источник:{Style.RESET_ALL} {source}")
    print(f"{Fore.CYAN}Обновлено:{Style.RESET_ALL} {updated}\n")

    for target in MINI_CLI_TARGETS:
        if target not in rates:
            print(f"{Fore.RED}  {target}: курс не найден{Style.RESET_ALL}")
            continue
        print(
            f"  1 {Fore.MAGENTA}{base}{Style.RESET_ALL} = "
            f"{Fore.YELLOW}{rates[target]:.6f}{Style.RESET_ALL} {target}"
        )


def mini_cli() -> None:
    base = input(
        f"{Fore.CYAN}Введите базовую валюту (например, USD): {Style.RESET_ALL}"
    ).strip().upper()

    if not base:
        print(f"{Fore.YELLOW}Валюта не указана.{Style.RESET_ALL}")
        return

    try:
        reference = get_reference_rates()
        validate_currency_code(base, reference)
        rates_data, source = load_or_update_rates(base)
    except (CurrencyApiError, InvalidCurrencyCodeError) as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    print_mini_cli_rates(base, rates_data, source)


def amount_converter_cli() -> None:
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Конвертер суммы{Style.RESET_ALL}")

    from_currency = input(f"{Fore.CYAN}Из валюты: {Style.RESET_ALL}").strip().upper()
    to_currency = input(f"{Fore.CYAN}В валюту: {Style.RESET_ALL}").strip().upper()
    amount_raw = input(f"{Fore.CYAN}Сумма: {Style.RESET_ALL}").strip().replace(",", ".")

    if not from_currency or not to_currency:
        print(f"{Fore.YELLOW}Укажите обе валюты.{Style.RESET_ALL}")
        return

    try:
        amount = float(amount_raw)
    except ValueError:
        print(f"{Fore.RED}Введите корректное число.{Style.RESET_ALL}")
        return

    if amount < 0:
        print(f"{Fore.RED}Сумма не может быть отрицательной.{Style.RESET_ALL}")
        return

    try:
        reference = get_reference_rates()
        validate_currency_code(from_currency, reference)
        validate_currency_code(to_currency, reference)
        result, rate = convert_amount(from_currency, to_currency, amount)
    except (CurrencyApiError, InvalidCurrencyCodeError, ValueError) as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.MAGENTA}{'═' * 45}")
    print(
        f"  {amount:.4f} {from_currency}  →  "
        f"{Fore.YELLOW}{result:.4f}{Style.RESET_ALL} {to_currency}"
    )
    print(f"{'═' * 45}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}Курс:{Style.RESET_ALL} "
        f"1 {from_currency} = {Fore.YELLOW}{rate:.4f}{Style.RESET_ALL} {to_currency}"
    )


def show_available_currencies(data: dict) -> None:
    base_currencies = get_base_currencies(data)
    print(f"\n{Fore.CYAN}Обновлено: {get_last_update(data)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}Основные валюты (исходные):{Style.RESET_ALL}")
    print("  " + ", ".join(f"{Fore.MAGENTA}{code}{Style.RESET_ALL}" for code in base_currencies))

    base = input(
        f"\n{Fore.CYAN}Показать целевые валюты для (Enter — все): {Style.RESET_ALL}"
    ).strip().upper()

    bases_to_show = [base] if base and base in base_currencies else base_currencies

    for base_code in bases_to_show:
        targets = get_target_currencies(data, base_code)
        print(f"\n{Fore.GREEN}{base_code}{Style.RESET_ALL} → {Fore.CYAN}{len(targets)} валют{Style.RESET_ALL}")
        for index in range(0, len(targets), 10):
            row = targets[index : index + 10]
            print("  " + ", ".join(f"{Fore.YELLOW}{code}{Style.RESET_ALL}" for code in row))


def show_conversion_interface(data: dict) -> None:
    base_currencies = get_base_currencies(data)
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Конвертация валют{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Данные: {get_last_update(data)}{Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}Основные валюты:{Style.RESET_ALL} "
        + ", ".join(f"{Fore.MAGENTA}{code}{Style.RESET_ALL}" for code in base_currencies)
    )

    from_currency = input(
        f"\n{Fore.CYAN}Исходная валюта ({', '.join(base_currencies)}): {Style.RESET_ALL}"
    ).strip().upper()
    if from_currency not in base_currencies:
        print(f"{Fore.RED}Выберите одну из основных валют: {', '.join(base_currencies)}{Style.RESET_ALL}")
        return

    try:
        validate_currency_code(from_currency, data[from_currency])
    except InvalidCurrencyCodeError as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    targets = get_target_currencies(data, from_currency)
    to_currency = input(
        f"{Fore.CYAN}Целевая валюта (из {len(targets)} доступных для {from_currency}): {Style.RESET_ALL}"
    ).strip().upper()

    try:
        validate_currency_code(to_currency, data[from_currency])
    except InvalidCurrencyCodeError as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    amount_raw = input(f"{Fore.CYAN}Сумма: {Style.RESET_ALL}").strip().replace(",", ".")
    try:
        amount = float(amount_raw)
    except ValueError:
        print(f"{Fore.RED}Введите корректное число.{Style.RESET_ALL}")
        return

    if amount < 0:
        print(f"{Fore.RED}Сумма не может быть отрицательной.{Style.RESET_ALL}")
        return

    try:
        result, rate = convert_currency(amount, from_currency, to_currency, data)
    except (ValueError, InvalidCurrencyCodeError) as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    print(f"\n{Fore.MAGENTA}{'═' * 45}")
    print(f"  {amount:.4f} {from_currency}  →  {result:.4f} {to_currency}")
    print(f"{'═' * 45}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Курс:{Style.RESET_ALL} 1 {from_currency} = {Fore.YELLOW}{rate:.4f}{Style.RESET_ALL} {to_currency}")
    print(f"{Fore.CYAN}Обратный курс:{Style.RESET_ALL} 1 {to_currency} = {Fore.YELLOW}{1 / rate:.4f}{Style.RESET_ALL} {from_currency}")


def validate_currency_cli() -> None:
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Проверка кода валюты{Style.RESET_ALL}")

    code = input(f"{Fore.CYAN}Введите код валюты (например, EUR): {Style.RESET_ALL}").strip()
    if not code:
        print(f"{Fore.YELLOW}Код не указан.{Style.RESET_ALL}")
        return

    try:
        reference = get_reference_rates()
        valid_code = validate_currency_code(code, reference)
    except (CurrencyApiError, InvalidCurrencyCodeError) as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return

    print(f"{Fore.GREEN}Код «{valid_code}» найден в списке доступных валют.{Style.RESET_ALL}")


def update_currency_rates() -> None:
    try:
        update_all_currency_rates()
    except CurrencyApiError as error:
        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}Данные обновлены в {DEFAULT_RATES_FILE}{Style.RESET_ALL}")


def try_load_rates_data() -> dict | None:
    if not file_exists():
        print(f"{Fore.RED}Файл {DEFAULT_RATES_FILE} не найден. Сначала обновите курсы (пункт 1).{Style.RESET_ALL}")
        return None

    try:
        return load_rates_data()
    except (json.JSONDecodeError, OSError) as error:
        print(f"{Fore.RED}Не удалось прочитать {DEFAULT_RATES_FILE}: {error}{Style.RESET_ALL}")
        return None


def main() -> None:
    print(f"{Fore.GREEN}{Style.BRIGHT}=== Конвертер валют ==={Style.RESET_ALL}\n")

    while True:
        print(f"{Fore.MAGENTA}1{Style.RESET_ALL} — Обновить курсы из API")
        print(f"{Fore.MAGENTA}2{Style.RESET_ALL} — Конвертировать валюту")
        print(f"{Fore.MAGENTA}3{Style.RESET_ALL} — Показать доступные валюты")
        print(f"{Fore.MAGENTA}4{Style.RESET_ALL} — Мини-CLI (RUB, EUR, GBP)")
        print(f"{Fore.MAGENTA}5{Style.RESET_ALL} — Конвертер суммы")
        print(f"{Fore.MAGENTA}6{Style.RESET_ALL} — Проверка кода валюты")
        print(f"{Fore.MAGENTA}0{Style.RESET_ALL} — Выход")

        try:
            choice = input(f"\n{Fore.CYAN}Выберите пункт меню (0–6): {Style.RESET_ALL}").strip()

            if choice == "0":
                print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
                break
            elif choice == "1":
                update_currency_rates()
            elif choice == "2":
                data = try_load_rates_data()
                if data:
                    show_conversion_interface(data)
            elif choice == "3":
                data = try_load_rates_data()
                if data:
                    show_available_currencies(data)
            elif choice == "4":
                mini_cli()
            elif choice == "5":
                amount_converter_cli()
            elif choice == "6":
                validate_currency_cli()
            else:
                print(f"{Fore.RED}Неверный выбор. Попробуйте снова.{Style.RESET_ALL}")
        except (CurrencyApiError, InvalidCurrencyCodeError, ValueError) as error:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
        except Exception as error:
            print(f"{Fore.RED}Произошла непредвиденная ошибка: {error}{Style.RESET_ALL}")

        print(f"\n{Fore.MAGENTA}{'─' * 45}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
