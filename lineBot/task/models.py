from datetime import datetime
import uuid
from django.db import models
from pydantic import BaseModel

from linenotify.models import Contact

# Create your models here.
class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField('Task_name', max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class createTaskModel(BaseModel):
    name: str
    description: str

class taskResponseModel(BaseModel):
    status_code: int
    id: str
    contact_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

