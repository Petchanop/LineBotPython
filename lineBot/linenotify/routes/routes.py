import json
import sys
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
from linenotify.models import Contact
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

async def create_contact(user_id: str):
    print("get or create user : " , user_id)
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    response = requests.get(url, headers=header)
    data = dict(json.loads(response._content.decode()))
    print(data)
    contact = await Contact.objects.acreate(line_id=data["userId"], display_name=data["displayName"])
    contact = {
        "status_code": status.HTTP_201_CREATED,
        "userId": data["userId"],
        "displayName": data["displayName"]
    }
    return contact

@router.post("/webhook")
async def handle_callback(request: Request):

    # hmac_sha256 = hmac.new(channel_secret.encode('utf-8'), channel_access_token.encode('utf-8'), hashlib.sha256).digest()
    signature = request.headers["X-Line-Signature"]
    # signature = base64.b64encode(hmac_sha256).decode('utf-8')
    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid signature")
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        try:
            if event.source.user_id:
                await Contact.objects.aget(line_id=event.source.user_id)
        except Contact.DoesNotExist:
            print(event)
            if event.type == "follow":
                await create_contact(event.source.user_id)
                await line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="Your contact has been created")],
                    )
                )
            if event.type == "block":
                await Contact.objects.adelete(line_id=event.source.user_id)
    #     if event.type == "message":
    #         result = await line_bot_api.reply_message(
    #             ReplyMessageRequest(
    #                 reply_token=event.reply_token,
    #                 messages=[TextMessage(text="May I help you?")],
    #             )
    #         )
    return {"message": "OK", "status_code": status.HTTP_200_OK}


@router.get("/profile/{userId}")
async def get_proflie(userId: str):
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api.line.me/v2/bot/profile/{userId}"
    response = requests.get(url, headers=header)
    print(response.__dict__)
    data = json.loads(response._content.decode())
    return { 'status_code': response.status_code, 'data': data }

@router.get("/profile/{lineId}")
async def get_profile_by_lineId(lineId: str):
    try:
        user = Contact.objects.aget(line_id=lineId)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="User not found")
    return { 'status_code': status.HTTP_200_OK}


from pydantic import BaseModel

class UserData(BaseModel):
    image_url: str
    message: str

@router.post("/send/message/{userId}")
async def send_message(userId: str, payload: UserData): 
    print(payload)
    image_url = payload.image_url
    message = payload.message
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    try:
        line_id = await Contact.objects.aget(user_id=userId)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    print("line id", line_id)
    body = {
        "to": line_id.line_id,
        "messages":[
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
    print(body)
    url = f"https://api.line.me/v2/bot/message/push"
    response = requests.post(url, headers=header, json=body)
    print(response.__dict__)
    return { 'status_code': response.status_code }



