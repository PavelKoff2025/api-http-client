"""Проверка критериев приёмки проекта валют."""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from api_client import CurrencyApiError, get_currency_rates
from cli import amount_converter_cli, validate_currency_cli
from storage import convert_amount, load_or_update_rates, read_from_file, save_to_file


def run_cli(func, inputs: list[str]) -> bool:
    old_stdin = sys.stdin
    sys.stdin = StringIO("\n".join(inputs) + "\n")
    try:
        func()
        return True
    except Exception:
        return False
    finally:
        sys.stdin = old_stdin


def main() -> None:
    test_file = "_acceptance_test.json"
    errors: list[str] = []

    def ok(name: str) -> None:
        print(f"✓ {name}")

    def fail(name: str, detail: str) -> None:
        print(f"✗ {name}: {detail}")
        errors.append(name)

    try:
        usd_data = get_currency_rates("USD")
        save_to_file({"USD": usd_data}, test_file)
        loaded = read_from_file(test_file)
        if loaded["USD"]["base_code"] == "USD":
            ok("currency_rate.json создаётся и читается")
        else:
            fail("currency_rate.json создаётся и читается", "неверные данные")

        Path(test_file).unlink(missing_ok=True)
        _, fresh_source = load_or_update_rates("USD", test_file)
        fresh_result, _ = convert_amount("USD", "RUB", 100, test_file)
        cached_result, _ = convert_amount("USD", "RUB", 100, test_file)
        _, cached_source = load_or_update_rates("USD", test_file)

        if fresh_source == "API" and cached_source == "файл" and fresh_result == cached_result:
            ok(f"USD→RUB: API={fresh_result:.4f}, кэш={cached_result:.4f}")
        else:
            fail(
                "USD→RUB кэш и API",
                f"API({fresh_source})={fresh_result}, кэш({cached_source})={cached_result}",
            )

        eur_file = "_acceptance_eur.json"
        Path(eur_file).unlink(missing_ok=True)
        _, eur_source = load_or_update_rates("EUR", eur_file)
        fresh_eur, _ = convert_amount("EUR", "GBP", 50, eur_file)
        cached_eur, _ = convert_amount("EUR", "GBP", 50, eur_file)
        _, eur_cached_source = load_or_update_rates("EUR", eur_file)

        if eur_source == "API" and eur_cached_source == "файл" and fresh_eur == cached_eur:
            ok(f"EUR→GBP: API={fresh_eur:.4f}, кэш={cached_eur:.4f}")
        else:
            fail(
                "EUR→GBP кэш и API",
                f"API({eur_source})={fresh_eur}, кэш({eur_cached_source})={cached_eur}",
            )

        if run_cli(amount_converter_cli, ["USD", "INVALID", "100"]):
            ok("невалидная валюта — без падения")
        else:
            fail("невалидная валюта", "необработанное исключение")

        with patch("storage.get_currency_rates", side_effect=CurrencyApiError("Ошибка сети")):
            with patch("storage.file_exists", return_value=False):
                if run_cli(validate_currency_cli, ["EUR"]):
                    ok("ошибка сети — без падения")
                else:
                    fail("ошибка сети", "необработанное исключение")

    finally:
        Path(test_file).unlink(missing_ok=True)
        Path("_acceptance_eur.json").unlink(missing_ok=True)

    print()
    if errors:
        print("ПРОВАЛ:", ", ".join(errors))
        sys.exit(1)

    print("Все критерии приёмки выполнены.")


if __name__ == "__main__":
    main()
