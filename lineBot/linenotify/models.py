import uuid
from django.db import models
from pydantic import BaseModel

#payload model
class UserData(BaseModel):
    image_url: str
    message: str

#response model
class ResponseUserData(BaseModel):
    status_code: int
    id: int
    user_id: str
    line_id: str
    whats_app_id: str
    display_name: str
    message: str
    enabled: bool
    task_limit: int | None

# Create your models here.
class Contact(models.Model):
    user_id = models.CharField(null=True, blank=True)
    line_id = models.CharField(null=True, blank=True)
    whats_app_id = models.CharField(null=True, blank=True)
    display_name = models.CharField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    task_limit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user_id or "Unnamed Contact"


