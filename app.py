import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# LINE credentials
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Weather API settings
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Taipei"
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
    msg = event.message.text.strip()

    if msg.startswith("☁️"):
        city = msg[1:].strip()
        report = get_weather_report_localized(city if city else "Taipei")
        report = "☁️ " + report

    elif msg.endswith("天氣"):
        city = msg[:-2].strip()
        report = get_weather_report_localized(city if city else "Taipei")
        report = "☁️ " + report

    else:
        return  # Do nothing if message doesn't match criteria

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=report)
    )




@app.route("/send_daily")
def send_daily():
    user_id = "YOUR_LINE_USER_ID"  # Replace with your personal LINE ID
    report = get_weather_report_localized()
    line_bot_api.push_message(user_id, TextSendMessage(text=report))
    return "Daily weather sent!"

def get_weather_report_localized(city="Taipei"):
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'zh_tw'
    }
    response = requests.get(WEATHER_URL, params=params)
    data = response.json()

    try:
        description = data['weather'][0]['description'].capitalize()
        temp_min = round(data['main']['temp_min'], 1)
        temp_max = round(data['main']['temp_max'], 1)
        humidity = data['main']['humidity']
        rain = "有降雨" if 'rain' in data else "無降雨"

        report = f"""🌤️ {city} 今日天氣預報：
天氣狀況：{description}
氣溫範圍：{temp_min}°C ~ {temp_max}°C
相對濕度：{humidity}%
降雨機率：{rain}"""
    except:
        report = f"⚠️ 無法取得「{city}」的天氣資料，請確認城市名稱是否正確。"

    return report


if __name__ == "__main__":
    app.run(debug=True, port=8000)
