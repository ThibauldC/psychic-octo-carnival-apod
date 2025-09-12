from dataclasses import dataclass
from datetime import datetime
import logging
import os

import requests
from slack_sdk import WebClient

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class AstronomyPicture:
    date: str
    explanation: str
    hdurl: str
    media_type: str
    service_version: str
    title: str
    url: str
    copyright: str | None = None

def get_astronomy_pic_from_nasa(today: datetime.date) -> AstronomyPicture:
    api_key = os.environ["NASA_API_KEY"]
    url = f"https://api.nasa.gov/planetary/apod?date={today}&api_key={api_key}"

    apod_resp = requests.get(url)
    if apod_resp.status_code == 200:
        pic = AstronomyPicture(**apod_resp.json())
        return pic
    else:
        LOGGER.error(f"Unable to get picture from NASA, status code {apod_resp.status_code}")
        raise Exception(apod_resp.text)


def send_astronomy_pic(pic: AstronomyPicture):
    bot_token = os.environ["SLACK_BOT_TOKEN"]
    channel_id = os.environ["SLACK_CHANNEL_ID"]
    client = WebClient(token=bot_token)
    client.chat_postMessage(
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


if __name__ == "__main__":
    pic = get_astronomy_pic_from_nasa(datetime.today().date())
    send_astronomy_pic(pic)
