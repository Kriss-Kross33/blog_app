from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['author', 'publish', 'created', 'status']
    raw_id_fields = ['author']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'body']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
