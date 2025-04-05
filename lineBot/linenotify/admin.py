from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'line_id', 'display_name', 'message']

admin.site.register(Contact, ContactAdmin)

# Register your models here.
