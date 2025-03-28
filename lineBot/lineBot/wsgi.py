"""
WSGI config for lineBot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lineBot.lineBot.settings')

application = get_wsgi_application()

apps.populate(settings.INSTALLED_APPS)

app = FastAPI(title='linebot integrate fast api with django', debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init(app: FastAPI):
    from lineBot.linenotify.routes.routes import router as linenotify_router
    from lineBot.lineBot.urls import api_router

    api_router.include_router(linenotify_router)
    app.include_router(api_router)

    if settings.MOUNT_DJANGO_APP:
        app.mount("/django", application)  # type:ignore

init(app)
