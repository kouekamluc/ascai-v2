"""
Models for community/forum app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class ForumCategory(models.Model):
    """Forum category model."""
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ForumThread(models.Model):
    """Forum thread model."""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name='threads',
        verbose_name=_('Category')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_threads',
        verbose_name=_('Author')
    )
    content = models.TextField(verbose_name=_('Content'))
    is_pinned = models.BooleanField(default=False, verbose_name=_('Pinned'))
    is_locked = models.BooleanField(default=False, verbose_name=_('Locked'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Views'))
    upvotes_count = models.PositiveIntegerField(default=0, verbose_name=_('Upvotes'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('community:thread_detail', kwargs={'slug': self.slug})


class ForumPost(models.Model):
    """Forum post/reply model."""
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Thread')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_posts',
        verbose_name=_('Author')
    )
    content = models.TextField(verbose_name=_('Content'))
    upvotes_count = models.PositiveIntegerField(default=0, verbose_name=_('Upvotes'))
    is_solution = models.BooleanField(default=False, verbose_name=_('Marked as Solution'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} in {self.thread.title}"


class ThreadUpvote(models.Model):
    """Thread upvote model."""
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='upvotes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['thread', 'user']


class PostUpvote(models.Model):
    """Post upvote model."""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='upvotes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']












