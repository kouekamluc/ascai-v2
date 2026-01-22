"""
URL configuration for community app.
"""
from django.urls import path
from .views import (
    ForumIndexView,
    ThreadListView,
    ThreadDetailView,
    ThreadCreateView,
    ThreadUpdateView,
    PostUpdateView,
    upvote_thread,
    upvote_post,
    toggle_thread_pin,
    toggle_thread_lock,
    toggle_post_solution,
    delete_thread,
    delete_post,
    PublicGroupListView,
    PublicGroupDetailView,
    group_join,
    GroupDiscussionListView
)

app_name = 'community'

urlpatterns = [
    path('', ForumIndexView.as_view(), name='index'),
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('threads/create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<slug:slug>/', ThreadDetailView.as_view(), name='thread_detail'),
    path('threads/<slug:slug>/edit/', ThreadUpdateView.as_view(), name='thread_edit'),
    path('threads/<slug:slug>/upvote/', upvote_thread, name='upvote_thread'),
    path('threads/<slug:slug>/pin/', toggle_thread_pin, name='toggle_thread_pin'),
    path('threads/<slug:slug>/lock/', toggle_thread_lock, name='toggle_thread_lock'),
    path('threads/<slug:slug>/delete/', delete_thread, name='delete_thread'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:post_id>/upvote/', upvote_post, name='upvote_post'),
    path('posts/<int:post_id>/solution/', toggle_post_solution, name='toggle_post_solution'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    # Public Community Groups
    path('groups/', PublicGroupListView.as_view(), name='group_list'),
    path('groups/<slug:slug>/', PublicGroupDetailView.as_view(), name='group_detail'),
    path('groups/<slug:slug>/join/', group_join, name='group_join'),
    path('groups/<slug:slug>/discussions/', GroupDiscussionListView.as_view(), name='group_discussions'),
]

