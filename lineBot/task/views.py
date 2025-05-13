from django.shortcuts import render

# Create your views here.

from fastapi import APIRouter, HTTPException, status

from linenotify.models import Contact
from task.models import Task

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/{userId}")
async def get_contact(userId: str):
    try:
        contact_object = await Contact.objects.aget(user_id=userId)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return { "status_code" : status.HTTP_200_OK, "data" : contact_object.all()}

@router.get("/{userId}/{taskName}")
async def get_contact_task(userId: str, taskName: str):
    try:
        contact_object = await Task.objects.aget(name=taskName)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return { "status_code" : status.HTTP_200_OK, "data" : contact_object.all()}

@router.post("/{userId}/{taskName}")
async def create_contact_task(userId: str, taskName: str):
    try:
        contact_object = await Task.objects.aget(name=taskName)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return { "status_code" : status.HTTP_200_OK, "data" : contact_object.all()}
