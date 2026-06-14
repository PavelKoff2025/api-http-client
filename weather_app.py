import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CACHE_FILE = Path("weather_cache.json")
CACHE_MAX_AGE = timedelta(hours=3)
RETRY_DELAYS = (1, 2, 4)


class NetworkError(Exception):
    pass


def _handle_api_error(response: requests.Response, context: str) -> None:
    if response.status_code == 401:
        print("Ошибка: невалидный API-ключ. Проверьте API_KEY в файле .env")
        return
    print(f"Ошибка {context}: HTTP {response.status_code}")


def _request_with_retries(url: str, context: str) -> requests.Response:
    for attempt in range(len(RETRY_DELAYS) + 1):
        if attempt > 0:
            delay = RETRY_DELAYS[attempt - 1]
            print(f"Повтор {attempt}/{len(RETRY_DELAYS)} через {delay}с...")
            time.sleep(delay)

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            if attempt < len(RETRY_DELAYS):
                print(f"Сетевая ошибка при {context}, повтор...")
                continue
            print(f"Ошибка сети при {context}")
            raise NetworkError from None

        if response.status_code == 429:
            if attempt < len(RETRY_DELAYS):
                print(f"Превышен лимит запросов (429) при {context}, повтор...")
                continue
            print(f"Ошибка {context}: HTTP 429")
            raise NetworkError from None

        return response

    raise NetworkError


def save_weather_cache(
    city: str | None,
    lat: float,
    lon: float,
    weather: dict,
    place_name: str,
) -> None:
    cache = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "place_name": place_name,
        "weather": weather,
    }
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_weather_cache() -> dict | None:
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def is_cache_fresh(cache: dict) -> bool:
    fetched_at = datetime.fromisoformat(cache["fetched_at"])
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - fetched_at < CACHE_MAX_AGE


def offer_cached_weather() -> tuple[dict, str] | None:
    cache = load_weather_cache()
    if cache is None:
        print("Кэш пуст.")
        return None
    if not is_cache_fresh(cache):
        print("Кэш устарел (данные старше 3 часов).")
        return None

    answer = input("Показать данные из кэша? (д/н): ").strip().lower()
    if answer not in ("д", "да", "y", "yes"):
        return None

    place_name = (
        cache.get("place_name")
        or cache.get("city")
        or cache["weather"].get("name", "кэш")
    )
    print(f"(данные из кэша от {cache['fetched_at']})")
    return cache["weather"], place_name


def _fetch_geocoding(city: str) -> dict | None:
    url = (
        f"https://api.openweathermap.org/geo/1.0/direct"
        f"?q={city}&limit=1&lang=ru&appid={API_KEY}"
    )
    response = _request_with_retries(url, f"получении координат для города «{city}»")

    if response.status_code != 200:
        _handle_api_error(response, "геокодинга")
        return None

    data = response.json()
    if not data:
        print(f"Город «{city}» не найден")
        return None

    return data[0]


def _city_display_name(geo: dict, fallback: str) -> str:
    local_names = geo.get("local_names") or {}
    return local_names.get("ru") or geo.get("name") or fallback


def get_coordinates(city: str) -> tuple[float, float] | None:
    geo = _fetch_geocoding(city)
    if geo is None:
        return None
    return geo["lat"], geo["lon"]


def get_weather_by_coordinates(lat: float, lon: float) -> dict | None:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
    )
    response = _request_with_retries(url, "получении погоды")

    if response.status_code != 200:
        _handle_api_error(response, "получения погоды")
        return None

    return response.json()


def get_current_weather(city: str) -> tuple[dict, str, float, float] | None:
    print(f"Получаем погоду для города: {city}")
    geo = _fetch_geocoding(city)
    if geo is None:
        return None
    weather = get_weather_by_coordinates(geo["lat"], geo["lon"])
    if weather is None:
        return None
    return weather, _city_display_name(geo, city), geo["lat"], geo["lon"]


def _print_weather(weather: dict, place_name: str) -> None:
    print(
        f"Погода в {place_name}: {weather['main']['temp']:.1f}°C, "
        f"{weather['weather'][0]['description']}"
    )


def _read_float(prompt: str) -> float | None:
    try:
        return float(input(prompt).strip().replace(",", "."))
    except ValueError:
        print("Некорректное число")
        return None


def run_cli() -> None:
    while True:
        print("\n1 — по городу")
        print("2 — по координатам")
        print("0 — выход")
        choice = input("Выберите режим: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        if choice == "1":
            city = input("Введите город: ").strip()
            if not city:
                print("Город не указан")
                continue
            try:
                result = get_current_weather(city)
            except NetworkError:
                cached = offer_cached_weather()
                if cached:
                    weather, place_name = cached
                    _print_weather(weather, place_name)
                continue
            if result:
                weather, city_name, lat, lon = result
                save_weather_cache(city, lat, lon, weather, city_name)
                _print_weather(weather, city_name)
            continue

        if choice == "2":
            lat = _read_float("Широта: ")
            if lat is None:
                continue
            lon = _read_float("Долгота: ")
            if lon is None:
                continue
            print(f"Получаем погоду для координат: {lat}, {lon}")
            try:
                weather = get_weather_by_coordinates(lat, lon)
            except NetworkError:
                cached = offer_cached_weather()
                if cached:
                    weather, place_name = cached
                    _print_weather(weather, place_name)
                continue
            if weather:
                place_name = weather["name"]
                save_weather_cache(None, lat, lon, weather, place_name)
                _print_weather(weather, place_name)
            continue

        print("Неизвестный режим. Введите 1, 2 или 0.")


if __name__ == "__main__":
    run_cli()
