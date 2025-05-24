from django.shortcuts import render

# Create your views here.

from fastapi import APIRouter, HTTPException, status
from asgiref.sync import sync_to_async

from linenotify.models import Contact
from task.models import Task, createTaskModel, taskResponseModel

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/{userId}", response_model=list[taskResponseModel])
async def get_task_by_contact(userId: str):
    try:
        
        response_task_list = []
        async for task in Task.objects.filter(contact_id__user_id=userId).select_related('contact_id'):
            response_task_list.append(
               taskResponseModel(
                    status_code=status.HTTP_200_OK,
                    id=task.id.__str__(),
                    contact_id=task.contact_id.__str__(),
                    name=task.name,
                    description=task.description,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
            )
    except Contact.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    except Task.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return response_task_list 

@router.get("/{userId}/{taskName}", response_model=taskResponseModel)
async def get_task_by_taskname(userId: str, taskName: str):
    try:
        task_object = await Task.objects.prefetch_related("contact_id").aget(name=taskName)
    except Task.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return taskResponseModel(
        status_code=status.HTTP_200_OK,
        id=task_object.id.__str__(),
        contact_id=task_object.contact_id.__str__(),
        name=task_object.name,
        description=task_object.description,
        created_at=task_object.created_at,
        updated_at=task_object.updated_at
    )

@router.post("/{userId}", response_model=taskResponseModel)
async def create_contact_task(userId: str, payload: createTaskModel):
    try:
        task_object = await Task.objects.aget(name=payload.name)
        if task_object:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task already exists")
    except Task.DoesNotExist:
        contact_id = await Contact.objects.aget(user_id=userId)
        task_object = await Task.objects.acreate(
            contact_id=contact_id,
            name=payload.name,
            description=payload.description,
        )
        response = taskResponseModel(
            status_code=status.HTTP_201_CREATED,
            id=task_object.id.__str__(),
            contact_id=task_object.contact_id.__str__(),
            name=task_object.name,
            description=task_object.description,
            created_at=task_object.created_at,
            updated_at=task_object.updated_at
        )
    return response 

@router.delete("/{userId}/{taskName}", response_model=taskResponseModel)
async def stop_task(userId: str, taskName: str):
    try:
        task_object = await Task.objects.prefetch_related("contact_id").aget(name=taskName)
        if task_object:
            await task_object.delete()
            response = taskResponseModel(
                status_code=status.HTTP_200_OK,
                id=task_object.id.__str__(),
                contact_id=task_object.contact_id.__str__(),
                name=task_object.name,
                description=task_object.description,
                created_at=task_object.created_at,
                updated_at=task_object.updated_at
            )
    except Task.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return response