from django.contrib import admin

from lineBot.task.models import Task

# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'contact_id', 'name', 'description', 'created_at', 'updated_at']

admin.site.register(Task, TaskAdmin)

