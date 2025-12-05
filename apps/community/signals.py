"""
Signals for community app to sync upvote counts.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ThreadUpvote, PostUpvote, ForumThread, ForumPost


@receiver([post_save, post_delete], sender=ThreadUpvote)
def sync_thread_upvote_count(sender, instance, **kwargs):
    """Sync thread upvote count from actual upvote records."""
    thread = instance.thread
    thread.upvotes_count = ThreadUpvote.objects.filter(thread=thread).count()
    thread.save(update_fields=['upvotes_count'])


@receiver([post_save, post_delete], sender=PostUpvote)
def sync_post_upvote_count(sender, instance, **kwargs):
    """Sync post upvote count from actual upvote records."""
    post = instance.post
    post.upvotes_count = PostUpvote.objects.filter(post=post).count()
    post.save(update_fields=['upvotes_count'])

