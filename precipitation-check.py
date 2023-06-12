import requests
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import config
import locale

# Yahoo天気APIのエンドポイントとアクセスキー
endpoint = "https://map.yahooapis.jp/weather/V1/place"
appid = config.yahoo_api_id

# 取得したい地点の緯度経度と期間（10分〜60分）
lat = config.lat
lon = config.lon
interval = "0,60"

# APIにリクエストを送信
response = requests.get(f"{endpoint}?coordinates={lon},{lat}&interval={interval}&output=json&appid={appid}")

# レスポンスをJSON形式でパース
data = response.json()

# 降水強度を取得
precipitation_data = data["Feature"][0]["Property"]["WeatherList"]["Weather"]
# ロケールを設定する
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

# 現在時刻を取得
now = datetime.now()

date_string = now.strftime("%Y年%m月%d日(%a)%H:%M")

rainCount = 0

subject=f"{date_string}\n"
text="\n```\n時間 (): 降水強度(mm/h)\n"

# 10分ごとに表示するためのループ
for i in range(13):
    # i番目のデータを取得
    d = precipitation_data[i]
    # データの時間をパース
    time = datetime.strptime(d["Date"], '%Y%m%d%H%M')
    # 現在時刻からの差分を計算
    diff = round((time - now).total_seconds() / 60 / 5) * 5
    # 時刻と時間を10分単位に丸めた上で、10分後、20分後、30分後、...という形式で表示する
    text += (f"{time.strftime('%Y/%m/%d %H:%M')} ({diff}分): {d['Rainfall']}\n")
    if d['Rainfall'] > 0.0 and i > 1:
        rainCount += 1

text +="```\n"

# Slackにメッセージを送信する関数
def send_message(channel, message, thread_ts=None):
    client = WebClient(token=config.slack_token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )
        print("Message sent: ", response['ts'])
    except SlackApiError as e:
        print("Error sending message: ", e)

#slackのタイムスタンプを得る関数
def get_previous_message_timestamp(channel):
    client = WebClient(token=config.slack_token)
    try:
        response = client.conversations_history(
            channel=channel,
            limit=1
        )
        messages = response['messages']
        if len(messages) > 0:
            previous_message = messages[0]
            return previous_message['ts']
    except SlackApiError as e:
        print("Error retrieving previous message: ", e)

previous_message_ts = get_previous_message_timestamp(channel=config.slack_channel)

if precipitation_data[2]['Rainfall'] == 0.0:
    if rainCount > 0:
        if precipitation_data[3]['Rainfall'] > 0.0:
            subject+="雨が降り出します"
            text+="<!channel>"
            message = f"{subject + text}"
            send_message(config.slack_channel, message)
        else:
            subject+="60分間の間に雨が降る恐れがあります"
            message = f"{subject + text}"
            send_message(config.slack_channel, message)
    else:
        subject+="しばらく雨は降りません"
else:
    if rainCount == 11:
        subject+="しばらく雨が続きます"
        message = f"{subject + text}"
        send_message(config.slack_channel, message, thread_ts=previous_message_ts)
    elif rainCount > 1:
        subject+="60分間の間に雨が止むタイミングがあります"
        message = f"{subject + text}"
        send_message(config.slack_channel, message, thread_ts=previous_message_ts)
    else:
        subject+="そろそろ雨が止みます"
        text+="<!channel>"
        message = f"{subject + text}"
        send_message(config.slack_channel, message)