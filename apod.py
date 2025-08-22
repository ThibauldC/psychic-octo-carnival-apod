from dataclasses import dataclass
from datetime import datetime
import os

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

@dataclass
class AstronomyPicture:
    copyright: str
    date: str
    explanation: str
    hdurl: str
    media_type: str
    service_version: str
    title: str
    url: str

def get_astronomy_pic_from_nasa(today: datetime.date):
    try:
        api_key = os.environ["NASA_API_KEY"]
    except KeyError:
        print("NASA_API_KEY not present")
    url = f"https://api.nasa.gov/planetary/apod?date={today}&api_key={api_key}"

    apod_resp = requests.get(url)
    if apod_resp.status_code == 200:
        pic = AstronomyPicture(**apod_resp.json())
        return pic
    else:
        print("TODO: send error to Slack")


def send_astronomy_pic(pic: AstronomyPicture):
    try:
        bot_token = os.environ["SLACK_BOT_TOKEN"]
        channel_id = os.environ["SLACK_CHANNEL_ID"]
    except KeyError as e:
        print("SLACK_BOT_TOKEN or SLACK_CHANNEL_ID not present")
        raise e
    client = WebClient(token=bot_token)
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Todays astronomy picture of the day* :rocket:*:*\n\n {pic.title}",
                    },
                },
                {"type": "divider"},
                {
                    "type": "image",
                    "image_url": pic.hdurl,
                    "alt_text": pic.explanation
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": pic.explanation,
                    },
                }
            ]
        )
        print(response)
    except SlackApiError as e:
        print(f"Error posting message: {e}")


if __name__ == "__main__":
    pic = get_astronomy_pic_from_nasa(datetime.today().date())
    send_astronomy_pic(pic)
