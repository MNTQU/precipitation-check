import os
from dotenv import load_dotenv
load_dotenv()

#Yahoo API
yahoo_api_id = os.environ.get("YAHOO_API_ID")
#slack API
slack_token = os.environ.get("SLACK_TOKEN")
#SLACK_CHANNEL
slack_channel = os.environ.get("SLACK_CHANNEL")
# 緯度経度
lat=os.environ.get("LAT")
lon=os.environ.get("LON")