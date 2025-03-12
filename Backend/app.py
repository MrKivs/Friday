# app.py (Backend)
from flask import Flask, request, jsonify
import requests
import re
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

class WeatherChatBot:
    def __init__(self):
        self.api_key = "ef3af68cf3fc7b222f1509ee2b94279a"  # Replace with your OpenWeatherMap API key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast?"
        self.state = None

    def _call_weather_api(self, city, is_forecast=False):
        url = self.forecast_url if is_forecast else self.base_url
        url += f"q={city}&appid={self.api_key}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def get_weather(self, city):
        data = self._call_weather_api(city)
        if not data:
            return None
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"Current weather in {city}: {temp}°C, {desc}."

    def get_forecast(self, city):
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
        match = re.search(r'(?:in|for) (.+)', user_input, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def process_input(self, user_input):
        user_input = user_input.lower()

        if re.search(r'\b(hi|hello|hey|morning|afternoon|evening|greetings|greeting|good morning|good afternoon|good evening|good day)\b', user_input):
            return "Hello! I'm your weather assistant. Ask about the weather or forecast!"
   
        if re.search(r'\b(how are you|how are you doing|how are you doing today|how are you today|what is your name|who are you)\b', user_input):
            return "Hello! I'm your weather assistant Friday. Here to provide you with weather support!"

        if re.search(r'\b(bye|exit|quit|goodbye|farewell|cya|see you)\b', user_input):
            return "Goodbye! Stay dry!"

        if re.search(r'\b(help|support|information|assistance|instructions|guidance|tutorial|directions)\b', user_input):
            return "I can provide current weather or a 5-day forecast. Try: 'Weather in Paris' or 'Forecast for London'."
        
        if re.search(r'\b(thanks|appreciated|great|nice|good|thank you|thank you very much|thank you so much|thank you so much for your help|thank you so much for your assistance|thank you so much for your support)\b', user_input):
            return "Always here to help you stay ahead."

        if re.search(r'\b(current weather|temperature|weather|climate|temperatures|conditions)\b', user_input):
            city = self._extract_city(user_input)
            if city:
                result = self.get_weather(city)
                return result if result else "City not found. Please try again."
            else:
                self.state = "weather"
                return "Which city's weather would you like to know?"

        if re.search(r'\b(forecast|5-day)\b', user_input):
            city = self._extract_city(user_input)
            if city:
                result = self.get_forecast(city)
                return result if result else "Forecast unavailable for this city."
            else:
                self.state = "forecast"
                return "Which city's forecast do you need?"

        if self.state:
            city = user_input.strip()
            if self.state == "weather":
                result = self.get_weather(city)
            elif self.state == "forecast":
                result = self.get_forecast(city)
            self.state = None
            return result if result else "Invalid city. Please try again."

        return "I didn't understand that. Ask about weather, forecast, or say 'help'."

bot = WeatherChatBot()

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = bot.process_input(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)