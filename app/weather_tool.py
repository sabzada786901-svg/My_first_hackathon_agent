import json
from urllib.parse import quote
from urllib.request import urlopen

from agents import function_tool


@function_tool
def get_current_weather(
    city: str,
    country: str = "Pakistan"
) -> dict:
    """
    Get current weather for any city.

    Example:
    get_current_weather(
        city="Faisalabad",
        country="Pakistan"
    )
    """

    city = city.strip()
    country = country.strip()

    if not city:
        return {
            "status": "error",
            "message": "City is required."
        }

    # ==========================================
    # 1. FIND CITY COORDINATES
    # ==========================================

    search_name = f"{city}, {country}"

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(search_name)}"
        "&count=1"
        "&language=en"
        "&format=json"
    )

    try:
        with urlopen(geocoding_url, timeout=10) as response:
            location_data = json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not find location: {str(e)}"
        }

    results = location_data.get("results", [])

    if not results:
        return {
            "status": "error",
            "message": (
                f"Could not find {city}, {country}."
            )
        }

    location = results[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    actual_city = location.get("name", city)
    actual_country = location.get("country", country)

    # ==========================================
    # 2. GET CURRENT WEATHER
    # ==========================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "precipitation,"
        "rain,"
        "weather_code,"
        "wind_speed_10m,"
        "wind_direction_10m"
        "&timezone=auto"
    )

    try:
        with urlopen(weather_url, timeout=10) as response:
            weather_data = json.loads(
                response.read().decode("utf-8")
            )

    except Exception as e:
        return {
            "status": "error",
            "message": f"Weather request failed: {str(e)}"
        }

    current = weather_data.get("current", {})

    weather_code = current.get("weather_code")

    # ==========================================
    # 3. WEATHER CONDITION
    # ==========================================

    condition = weather_code_description(weather_code)

    # ==========================================
    # 4. RETURN WEATHER
    # ==========================================

    return {
        "status": "success",

        "location": {
            "city": actual_city,
            "country": actual_country,
        },

        "current_weather": {
            "time": current.get("time"),

            "temperature_c": current.get(
                "temperature_2m"
            ),

            "feels_like_c": current.get(
                "apparent_temperature"
            ),

            "humidity_percent": current.get(
                "relative_humidity_2m"
            ),

            "precipitation_mm": current.get(
                "precipitation"
            ),

            "rain_mm": current.get(
                "rain"
            ),

            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            ),

            "wind_direction_degree": current.get(
                "wind_direction_10m"
            ),

            "condition": condition,
        },

        "source": "Open-Meteo"
    }


def weather_code_description(code):
    """
    Convert Open-Meteo weather code
    into a readable weather condition.
    """

    conditions = {
        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        66: "Light freezing rain",
        67: "Heavy freezing rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        77: "Snow grains",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",

        85: "Slight snow showers",
        86: "Heavy snow showers",

        95: "Thunderstorm",

        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return conditions.get(
        code,
        "Unknown weather condition"
    )