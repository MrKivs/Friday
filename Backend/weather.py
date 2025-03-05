import requests
import re
import locale
locale.setlocale(locale.LC_ALL, '')

class WeatherChatBot:
    def __init__(self):
        self.api_key = "ef3af68cf3fc7b222f1509ee2b94279a"  # API key from OpenWeatherMap
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast?"
        self.state = None  # Tracks conversation state
        self.current_intent = None  # Tracks the current intent

    def _call_weather_api(self, city, is_forecast=False):
        """Fetches weather data from OpenWeatherMap API."""
        url = self.forecast_url if is_forecast else self.base_url
        url += f"q={city}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def get_weather(self, city):
        """Fetches current weather for a city."""
        data = self._call_weather_api(city)
        if not data:
            return None
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"Current weather in {city}: {temp}°C, {desc}."

    def get_forecast(self, city):
        """Fetches 5-day weather forecast for a city."""
        data = self._call_weather_api(city, is_forecast=True)
        if not data:
            return None
        forecast = {}
        for entry in data['list']:
            date = entry['dt_txt'].split()[0]
            if date not in forecast:
                temp = entry['main']['temp']
                desc = entry['weather'][0]['description']
                forecast[date] = f"{date}: {temp}°C, {desc}"
        return "5-Day Forecast:\n" + "\n".join(forecast.values())

    def _extract_city(self, user_input):
        """Extracts city name from user input using regex."""
        match = re.search(r'(?:in|for) (.+)', user_input, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def process_input(self, user_input):
        user_input = user_input.lower()

        # Handle greetings
        if re.search(r'\b(hi|hello|hey)\b', user_input):
            return "Hello! I'm your weather assistant. Ask about the weather or forecast!"

        # Handle goodbye
        if re.search(r'\b(bye|exit|quit)\b', user_input):
            return "Goodbye! Stay dry!"

        # Handle help
        if re.search(r'\b(help|support)\b', user_input):
            return "I can provide current weather or a 5-day forecast. Try: 'Weather in Paris' or 'Forecast for London'."

        # Handle current weather
        if re.search(r'\b(current weather|temperature|weather)\b', user_input):
            city = self._extract_city(user_input)
            if city:
                result = self.get_weather(city)
                return result if result else "City not found. Please try again."
            else:
                self.state = "weather"
                return "Which city's weather would you like to know?"

        # Handle forecast
        if re.search(r'\b(forecast|5-day)\b', user_input):
            city = self._extract_city(user_input)
            if city:
                result = self.get_forecast(city)
                return result if result else "Forecast unavailable for this city."
            else:
                self.state = "forecast"
                return "Which city's forecast do you need?"

        # Handle follow-up city input
        if self.state:
            city = user_input.strip()
            if self.state == "weather":
                result = self.get_weather(city)
            elif self.state == "forecast":
                result = self.get_forecast(city)
            self.state = None
            return result if result else "Invalid city. Please try again."

        # Fallback for unrecognized queries
        return "I didn't understand that. Ask about weather, forecast, or say 'help'."

def main():
    bot = WeatherChatBot()
    print("Bot: " + bot.process_input("hello"))
    while True:
        user_input = input("You: ")
        response = bot.process_input(user_input)
        print("Bot:", response)
        if "goodbye" in response.lower():
            break

if __name__ == "__main__":
    main()