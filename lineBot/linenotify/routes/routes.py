import json
from typing import Union

import os
import sys
import hmac
import hashlib
import base64

from fastapi import APIRouter, Request, Response, status, FastAPI, HTTPException

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import requests
from django.conf import settings
from rich import print


if settings.CHANNEL_SECRET is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if settings.CHANNEL_ACCESS_TOKEN is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

configuration = Configuration(access_token=settings.CHANNEL_ACCESS_TOKEN)

router = APIRouter(tags=["linenotify"])
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(settings.CHANNEL_SECRET)


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/webhook")
async def handle_callback(request: Request):

    # hmac_sha256 = hmac.new(channel_secret.encode('utf-8'), channel_access_token.encode('utf-8'), hashlib.sha256).digest()
    signature = request.headers["X-Line-Signature"]
    # signature = base64.b64encode(hmac_sha256).decode('utf-8')

    # get request body as text
    body = await request.body()
    body = body.decode()
    print("body", body)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue

        # result = await line_bot_api.reply_message(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=event.message.text)],
        #     )
        # )

    return {"message": "OK", "status_code": status.HTTP_200_OK}


@router.get("/profile/{userId}")
async def get_proflie(userId: int):
    # user_id = await request.body()['userId']
    user_id = "Ufad02a204eaa97d49a885357c90b8c22"
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    print("header", header)
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    print('url', url)
    response = requests.get(url, headers=header)
    print(response.__dict__)
    data = json.loads(response._content.decode())
    return { 'status_code': response.status_code, 'data': data }

@router.post("/send/message/{userId}")
async def send_message(userId: int, request: Request):  
    image_url = await request.body()['image_url']
    message = await request.body()['message']
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    body = {
        "to": userId,
        "message":[
             {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            },
            {
                "type": "text",
                "text": message,
            }
        ]
    }
    url = f"https://api.line.me/v2/bot/message/push"
    response = requests.post(url, header=header, body=body)
    return { 'status_code': response.status_code }


# # "userId":"Ufad02a204eaa97d49a885357c90b8c22"
# curl -v -X GET https://api.line.me/v2/bot/profile/Ufad02a204eaa97d49a885357c90b8c22 \
# -H 'Authorization: Bearer xqh4XTuhS+iDFd72xBvReEGspLmT7wiIbme2ySkH4EI3UrqDTbi6K6VPyD3lvEljM4XkX2BnsiOGc9/+2ysD8gZ1b6PL9urcPtbANBcIu/GS12PLDkN7hWFTVJqA
# dpPo2XBuvuY7Ud+rm85jKJeOCwdB04t89/1O/w1cDnyilFU='

if __name__ == "__main__":
    app.run()
