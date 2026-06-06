from google.adk.agents import Agent
from datetime import datetime
import pytz
import requests
from serpapi import GoogleSearch
import wikipedia
import pyjokes
from countryinfo import CountryInfo

SERPAPI_KEY = "0d965c6ebc79c10c792d10e7ee5d22d5d09ceb8d1dc23125eb92c0f5b873e203"

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    timezones = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "india": "Asia/Kolkata",
        "chennai": "Asia/Kolkata",
        "madurai": "Asia/Kolkata",
    }
    tz_name = timezones.get(city.lower(), "UTC")
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    return {
        "city": city,
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%A, %B %d %Y")
    }

def get_weather(city: str) -> dict:
    """Returns current weather for a specified city."""
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    data = response.json()
    current = data["current_condition"][0]
    return {
        "city": city,
        "temperature_c": current["temp_C"],
        "temperature_f": current["temp_F"],
        "condition": current["weatherDesc"][0]["value"],
        "humidity": current["humidity"],
        "feels_like_c": current["FeelsLikeC"],
    }

def calculator(operation: str, a: float, b: float) -> dict:
    """Performs basic math. Operations: add, subtract, multiply, divide."""
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero!"}
        result = a / b
    else:
        return {"error": "Unknown operation!"}
    return {"operation": operation, "a": a, "b": b, "result": result}

def google_search(query: str) -> dict:
    """Searches Google and returns top results."""
    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3,
    })
    results = search.get_dict()
    organic = results.get("organic_results", [])
    return {
        "query": query,
        "results": [
            {
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "link": r.get("link"),
            }
            for r in organic[:3]
        ]
    }

def currency_converter(amount: float, from_currency: str, to_currency: str) -> dict:
    """Converts currency from one type to another."""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
    response = requests.get(url)
    data = response.json()
    rate = data["rates"].get(to_currency.upper())
    if not rate:
        return {"error": f"Currency {to_currency} not found!"}
    converted = round(amount * rate, 2)
    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "converted": converted,
        "rate": rate,
    }

def get_news(topic: str) -> dict:
    """Gets latest news for a given topic."""
    url = f"https://newsdata.io/api/1/news?apikey=pub_demo&q={topic}&language=en"
    response = requests.get(url)
    data = response.json()
    articles = data.get("results", [])[:3]
    return {
        "topic": topic,
        "news": [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "source": a.get("source_id"),
            }
            for a in articles
        ]
    }

def search_wikipedia(query: str) -> dict:
    """Searches Wikipedia and returns a summary."""
    try:
        summary = wikipedia.summary(query, sentences=3)
        return {"query": query, "summary": summary}
    except Exception as e:
        return {"error": str(e)}

def tell_joke() -> dict:
    """Returns a random joke."""
    joke = pyjokes.get_joke()
    return {"joke": joke}

def get_country_info(country: str) -> dict:
    """Returns information about a country."""
    try:
        info = CountryInfo(country)
        data = info.info()
        return {
            "country": country,
            "capital": data.get("capital"),
            "population": data.get("population"),
            "area": data.get("area"),
            "currencies": data.get("currencies"),
            "languages": data.get("languages"),
            "region": data.get("region"),
        }
    except Exception as e:
        return {"error": str(e)}

def days_between_dates(date1: str, date2: str) -> dict:
    """Calculates days between two dates. Format: YYYY-MM-DD"""
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        return {"date1": date1, "date2": date2, "days_between": diff}
    except Exception as e:
        return {"error": str(e)}

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash-lite",
    description="A powerful assistant with 10 tools.",
    instruction="""You are a helpful assistant. Use the right tool for each question:
    - get_current_time: for time questions
    - get_weather: for weather questions
    - calculator: for math questions
    - google_search: for internet searches
    - currency_converter: for currency conversion
    - get_news: for latest news
    - search_wikipedia: for general knowledge
    - tell_joke: for jokes
    - get_country_info: for country information
    - days_between_dates: for date calculations""",
    tools=[
        get_current_time,
        get_weather,
        calculator,
        google_search,
        currency_converter,
        get_news,
        search_wikipedia,
        tell_joke,
        get_country_info,
        days_between_dates,
    ],
)