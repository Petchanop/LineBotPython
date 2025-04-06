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

async def create_group_contact(event, group_id: str):
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api.line.me/v2/bot/group/{group_id}/summary"
    response = requests.get(url, headers=header)
    data = dict(json.loads(response._content.decode()))
    contact = await Contact.objects.acreate(
        line_id=data["groupId"], display_name=data["groupName"]
    )
    contact = {
        "status_code": status.HTTP_201_CREATED,
        "userId": data["groupId"],
        "displayName": data["groupName"],
    }
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="Your group contact has been created")],
        )
    )
    return contact

async def create_contact(event, user_id: str):
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    response = requests.get(url, headers=header)
    data = dict(json.loads(response._content.decode()))
    contact = await Contact.objects.acreate(
        line_id=data["userId"], display_name=data["displayName"]
    )
    contact = {
        "status_code": status.HTTP_201_CREATED,
        "userId": data["userId"],
        "displayName": data["displayName"],
    }
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="Your contact has been created")],
        )
    )
    return contact


@router.post("/webhook")
async def handle_callback(request: Request):

    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid signature"
        )
    for event in events:
        print(event)
        match event.type:
            case "follow":
                try:
                    if event.source.user_id:
                        await Contact.objects.aget(line_id=event.source.user_id)
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="May I help you?")],
                        )
                except Contact.DoesNotExist:
                    await create_contact(event, event.source.user_id)
            case "unfollow":
                contact = await Contact.objects.aget(line_id=event.source.user_id)
                await contact.adelete()
            case "join":
                try:
                    if event.source.group_id:
                        await Contact.objects.aget(line_id=event.source.group_id)
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="Thank you for inviting me")],
                        )
                except Contact.DoesNotExist:
                    await create_contact(event, event.source.group_id)
            case "leave":
                contact = await Contact.objects.aget(line_id=event.source.group_id)
                await contact.adelete()
    return {"message": "OK", "status_code": status.HTTP_200_OK}


@router.get("/profile/{userId}")
async def get_proflie(userId: str):
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api.line.me/v2/bot/profile/{userId}"
    response = requests.get(url, headers=header)
    data = json.loads(response._content.decode())
    return {"status_code": response.status_code, "data": data}


@router.get("/profile/{lineId}")
async def get_profile_by_lineId(lineId: str):
    try:
        user = Contact.objects.aget(line_id=lineId)
    except Contact.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"status_code": status.HTTP_200_OK}


from pydantic import BaseModel


class UserData(BaseModel):
    image_url: str
    message: str

@router.post("/send/message/{userId}")
async def send_message(userId: str, payload: UserData):
    image_url = payload.image_url
    message = payload.message
    header = {"Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"}
    try:
        line_object = await Contact.objects.aget(user_id=userId)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    body = {
        "to": line_object.line_id,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url,
            },
            {
                "type": "text",
                "text": message,
            },
       
        ],
    }
    if line_object.message:
        body["messages"].append({
                "type": "text",
                "text": line_object.message
            })
    url = f"https://api.line.me/v2/bot/message/push"
    response = requests.post(url, headers=header, json=body)
    return {"status_code": response.status_code}
