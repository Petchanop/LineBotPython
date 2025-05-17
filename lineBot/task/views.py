from django.shortcuts import render

# Create your views here.

from fastapi import APIRouter, HTTPException, status

from linenotify.models import Contact
from task.models import Task, createTaskModel, taskResponseModel

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/{userId}", reponse_model=[taskResponseModel])
async def get_task_by_contact(userId: str):
    try:
        contact_object = await Contact.objects.aget(user_id=userId)
        task_object = await Task.objects.aget(contact_id=contact_object)
    except Contact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return { "status_code" : status.HTTP_200_OK, "data" : task_object.all()}

@router.get("/{userId}/{taskName}", response_model=taskResponseModel)
async def get_task_by_taskname(userId: str, taskName: str):
    try:
        task_object = await Task.objects.aget(name=taskName)
    except Task.DoesNotExist:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return { "status_code" : status.HTTP_200_OK, "data" : task_object}

@router.post("/{userId}", response_model=taskResponseModel)
async def create_contact_task(userId: str, payload: createTaskModel):
    try:
        task_object = await Task.objects.aget(name=payload.name)
        if task_object:
            raise HTTPException(status_code=400, detail="Task already exists")
    except Task.DoesNotExist:
        contact_id = await Contact.objects.aget(user_id=userId)
        task_object = await Task.objects.acreate(
            contact_id=contact_id,
            name=payload.name,
            description=payload.description,
        )
    
    return { "status_code" : status.HTTP_200_OK, "data" : task_object}
