"""
ASGI config for lineBot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.apps import apps
from django.conf import settings
import lineBot.lineBot.settings as lineBot_settings 
from django.core.asgi import get_asgi_application
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lineBot.lineBot.settings')
application = get_asgi_application()

try:
    settings.configure(default_settings=lineBot_settings, DEBUG=True)
except RuntimeError:  # Avoid: 'Settings already configured.'
    pass

apps.populate(settings.INSTALLED_APPS)

app = FastAPI(title='linebot integrate fast api with django', debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init(app: FastAPI):
    from linenotify.routes.routes import router as linenotify_router
    from lineBot.lineBot.urls import api_router

    api_router.include_router(linenotify_router)
    app.include_router(api_router)

    if settings.MOUNT_DJANGO_APP:
        app.mount("/django", application)  # type:ignore

init(app)
