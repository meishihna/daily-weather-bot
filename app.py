import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# LINE Bot credentials
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# OpenWeatherMap API credentials
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Taipei"  # You can change this to your preferred city
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    weather_report = get_weather_report()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=weather_report)
    )

def get_weather_report():
    params = {
        'q': CITY,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'en'
    }
    response = requests.get(WEATHER_URL, params=params)
    weather = response.json()

    description = weather['weather'][0]['description'].capitalize()
    temp = weather['main']['temp']
    humidity = weather['main']['humidity']
    report = f"🌤️ Weather in {CITY}:\n\n{description}\nTemperature: {temp}°C\nHumidity: {humidity}%"

    return report

if __name__ == "__main__":
    app.run(debug=True, port=8000)
