from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
