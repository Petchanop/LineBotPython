from django.db import models

# Create your models here.
class Contact(models.Model):
    user_id = models.CharField(null=True, blank=True)
    line_id = models.CharField(null=True, blank=True)
    display_name = models.CharField(null=True, blank=True)

