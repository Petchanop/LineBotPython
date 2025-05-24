from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ['user_id',  'line_id', 'whats_app_id', 'display_name', 'message', 'enabled', 'task_limit']
    search_fields = ['user_id', 'line_id', 'whats_app_id', 'display_name']
    list_filter = ['enabled']

admin.site.register(Contact, ContactAdmin)

# Register your models here.
