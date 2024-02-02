from django.contrib import admin
from .models import Comment, Ipr, Task


@admin.register(Ipr)
class IprAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'employee',
        'author',
        'description',
        'status',
        'created_date',
        'end_date',
        # 'tasks'
    )
    search_fields = ('title', 'employee', 'author',)
    list_filter = ('id', 'title', 'employee', 'author')
    empty_value_display = '-пусто-'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
