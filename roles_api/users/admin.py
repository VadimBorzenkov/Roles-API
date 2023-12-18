from django.contrib import admin

from users.models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', 'completed')
