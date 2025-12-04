"""
Admin configuration for community app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import ForumCategory, ForumThread, ForumPost, ThreadUpvote, PostUpvote


@admin.register(ForumCategory)
class ForumCategoryAdmin(ModelAdmin):
    """Admin interface for ForumCategory."""
    list_display = ['name', 'order', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ForumThread)
class ForumThreadAdmin(ModelAdmin):
    """Admin interface for ForumThread."""
    list_display = ['title', 'category', 'author', 'is_pinned', 'is_locked', 'views_count', 'upvotes_count', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']


@admin.register(ForumPost)
class ForumPostAdmin(ModelAdmin):
    """Admin interface for ForumPost."""
    list_display = ['thread', 'author', 'is_solution', 'upvotes_count', 'created_at']
    list_filter = ['is_solution', 'created_at']
    search_fields = ['content', 'author__username', 'thread__title']
    raw_id_fields = ['thread', 'author']


admin.site.register(ThreadUpvote)
admin.site.register(PostUpvote)



















