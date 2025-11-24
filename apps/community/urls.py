"""
URL configuration for community app.
"""
from django.urls import path
from .views import (
    ForumIndexView,
    ThreadListView,
    ThreadDetailView,
    ThreadCreateView,
    upvote_thread,
    upvote_post
)

app_name = 'community'

urlpatterns = [
    path('', ForumIndexView.as_view(), name='index'),
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('threads/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<slug:slug>/', ThreadDetailView.as_view(), name='thread_detail'),
    path('threads/<slug:slug>/upvote/', upvote_thread, name='upvote_thread'),
    path('posts/<int:post_id>/upvote/', upvote_post, name='upvote_post'),
]

