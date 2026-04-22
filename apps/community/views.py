"""
Views for community/forum app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.db.models import Count, Q, F
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import ForumCategory, ForumThread, ForumPost, ThreadUpvote, PostUpvote
from .forms import ThreadForm, PostForm
from apps.dashboard.models import CommunityGroup, GroupDiscussion


def _get_thread_posts_context(thread, user):
    """Build the replies section context."""
    context = {
        'thread': thread,
        'posts': thread.posts.select_related('author').order_by('-is_solution', 'created_at'),
        'user': user,
    }

    if user.is_authenticated:
        context['upvoted_post_ids'] = list(
            PostUpvote.objects.filter(
                user=user,
                post__thread=thread
            ).values_list('post_id', flat=True)
        )
    else:
        context['upvoted_post_ids'] = []

    return context


def _render_posts_section(request, thread, status=200):
    """Render the full replies section for HTMX updates."""
    return render(
        request,
        'community/partials/posts_section.html',
        _get_thread_posts_context(thread, request.user),
        status=status,
    )


class ForumIndexView(ListView):
    """Main forum page with categories."""
    model = ForumCategory
    template_name = 'community/index.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ForumCategory.objects.annotate(
            thread_count=Count('threads')
        ).order_by('order', 'name')


class ThreadListView(ListView):
    """List view for forum threads."""
    model = ForumThread
    template_name = 'community/thread_list.html'
    context_object_name = 'threads'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ForumThread.objects.annotate(
            post_count=Count('posts', distinct=True)
        ).select_related('author', 'category')
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset.order_by('-is_pinned', '-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get('category')
        if category_slug:
            context['category'] = get_object_or_404(ForumCategory, slug=category_slug)
        # Add all categories for filter UI
        context['categories'] = ForumCategory.objects.all().order_by('order', 'name')
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'community/partials/thread_list_partial.html'
        return super().get_template_names()


class ThreadDetailView(DetailView):
    """Detail view for forum thread with posts."""
    model = ForumThread
    template_name = 'community/thread_detail.html'
    context_object_name = 'thread'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return ForumThread.objects.select_related('author', 'category').prefetch_related('posts__author')
    
    def get_object(self, queryset=None):
        """Increment views count when thread is viewed."""
        obj = super().get_object(queryset)
        if self.request.method == 'GET':
            ForumThread.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
            obj.refresh_from_db()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_get_thread_posts_context(self.object, self.request.user))
        
        # Check if user has upvoted
        if self.request.user.is_authenticated:
            context['has_upvoted_thread'] = ThreadUpvote.objects.filter(
                thread=self.object,
                user=self.request.user
            ).exists()
        else:
            context['has_upvoted_thread'] = False
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle post creation via HTMX."""
        self.object = self.get_object()
        if not request.user.is_authenticated:
            login_response = redirect_to_login(request.get_full_path())
            if request.headers.get('HX-Request'):
                response = HttpResponse(status=401)
                response['HX-Redirect'] = login_response.url
                return response
            return login_response

        if self.object.is_locked:
            return JsonResponse({'error': _('Thread is locked.')}, status=403)
        
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = self.object
            post.author = request.user
            post.save()
            # Update thread updated_at
            from django.utils import timezone
            ForumThread.objects.filter(pk=self.object.pk).update(updated_at=timezone.now())
            self.object.refresh_from_db()
            return _render_posts_section(request, self.object)
        return JsonResponse({'error': _('Invalid form data.')}, status=400)


class ThreadCreateView(LoginRequiredMixin, CreateView):
    """Create new thread view."""
    model = ForumThread
    form_class = ThreadForm
    template_name = 'community/thread_create.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def upvote_thread(request, slug):
    """Upvote/unupvote thread (HTMX endpoint)."""
    thread = get_object_or_404(ForumThread, slug=slug)
    upvote, created = ThreadUpvote.objects.get_or_create(
        thread=thread,
        user=request.user
    )
    
    if not created:
        upvote.delete()
        has_upvoted = False
    else:
        has_upvoted = True
    
    # Refresh thread to get updated count from signals
    thread.refresh_from_db()
    
    if request.headers.get('HX-Request'):
        return render(request, 'community/partials/upvote_button.html', {
            'thread': thread,
            'has_upvoted': has_upvoted
        })
    
    return JsonResponse({'upvoted': has_upvoted, 'count': thread.upvotes_count})


@login_required
@require_http_methods(["POST"])
def upvote_post(request, post_id):
    """Upvote/unupvote post (HTMX endpoint)."""
    post = get_object_or_404(ForumPost, id=post_id)
    upvote, created = PostUpvote.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        upvote.delete()
        has_upvoted = False
    else:
        has_upvoted = True
    
    # Refresh post to get updated count from signals
    post.refresh_from_db()
    
    if request.headers.get('HX-Request'):
        return render(request, 'community/partials/post_upvote_button.html', {
            'post': post,
            'has_upvoted': has_upvoted
        })
    
    return JsonResponse({'upvoted': has_upvoted, 'count': post.upvotes_count})


@login_required
@require_http_methods(["POST"])
def toggle_thread_pin(request, slug):
    """Toggle thread pin status (Admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    thread = get_object_or_404(ForumThread, slug=slug)
    thread.is_pinned = not thread.is_pinned
    thread.save()
    
    if request.headers.get('HX-Request'):
        return render(request, 'community/partials/moderation_buttons.html', {
            'thread': thread,
            'user': request.user
        })
    
    return JsonResponse({'pinned': thread.is_pinned})


@login_required
@require_http_methods(["POST"])
def toggle_thread_lock(request, slug):
    """Toggle thread lock status (Admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    thread = get_object_or_404(ForumThread, slug=slug)
    thread.is_locked = not thread.is_locked
    thread.save()
    
    if request.headers.get('HX-Request'):
        return render(request, 'community/partials/moderation_buttons.html', {
            'thread': thread,
            'user': request.user
        })
    
    return JsonResponse({'locked': thread.is_locked})


@login_required
@require_http_methods(["POST"])
def delete_thread(request, slug):
    """Delete thread (Author or Admin only)."""
    thread = get_object_or_404(ForumThread, slug=slug)
    
    # Check if user is author or staff
    if not (request.user == thread.author or request.user.is_staff):
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    thread.delete()
    messages.success(request, _('Thread deleted successfully.'))
    
    # For HTMX requests, return a redirect response
    if request.headers.get('HX-Request'):
        from django.http import HttpResponse
        response = HttpResponse('')
        response['HX-Redirect'] = reverse_lazy('community:thread_list')
        return response
    
    return redirect('community:thread_list')


@login_required
@require_http_methods(["POST"])
def delete_post(request, post_id):
    """Delete post (Author or Admin only)."""
    post = get_object_or_404(ForumPost, id=post_id)
    
    # Check if user is author or staff
    if not (request.user == post.author or request.user.is_staff):
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    thread = post.thread
    post.delete()
    messages.success(request, _('Post deleted successfully.'))
    
    if request.headers.get('HX-Request'):
        return _render_posts_section(request, thread)
    
    return redirect('community:thread_detail', slug=thread.slug)


class ThreadUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update thread view (Author or Admin only)."""
    model = ForumThread
    form_class = ThreadForm
    template_name = 'community/thread_edit.html'
    
    def test_func(self):
        """Check if user is author or staff."""
        thread = self.get_object()
        return self.request.user == thread.author or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, _('Thread updated successfully.'))
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update post view (Author or Admin only)."""
    model = ForumPost
    form_class = PostForm
    template_name = 'community/post_edit.html'
    
    def test_func(self):
        """Check if user is author or staff."""
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def get_success_url(self):
        return self.object.thread.get_absolute_url()
    
    def form_valid(self, form):
        messages.success(self.request, _('Post updated successfully.'))
        return super().form_valid(form)


@login_required
@require_http_methods(["POST"])
def toggle_post_solution(request, post_id):
    """Toggle post solution status (Thread author or Admin only)."""
    post = get_object_or_404(ForumPost, id=post_id)
    thread = post.thread
    
    # Check if user is thread author or staff
    if not (request.user == thread.author or request.user.is_staff):
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    # If marking as solution, unmark other solutions in the thread
    if not post.is_solution:
        ForumPost.objects.filter(thread=thread, is_solution=True).update(is_solution=False)
    
    post.is_solution = not post.is_solution
    post.save()
    
    if request.headers.get('HX-Request'):
        return _render_posts_section(request, thread)
    
    return JsonResponse({'is_solution': post.is_solution})


# Public Community Groups Views

class PublicGroupListView(ListView):
    """Public groups directory."""
    model = CommunityGroup
    template_name = 'community/groups/list.html'
    context_object_name = 'groups'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = CommunityGroup.objects.filter(is_public=True).annotate(
            member_count_annotated=Count('members')
        )
        
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        featured = self.request.GET.get('featured')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset.order_by('-featured', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['featured_groups'] = CommunityGroup.objects.filter(
            is_public=True,
            featured=True
        ).annotate(
            member_count_annotated=Count('members')
        )[:6]
        
        # Get user's group memberships if logged in
        if self.request.user.is_authenticated:
            context['user_group_ids'] = list(
                self.request.user.community_groups.values_list('id', flat=True)
            )
        else:
            context['user_group_ids'] = []
        
        return context


class PublicGroupDetailView(DetailView):
    """Public group detail page."""
    model = CommunityGroup
    template_name = 'community/groups/detail.html'
    context_object_name = 'group'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return CommunityGroup.objects.filter(is_public=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent discussions
        context['recent_discussions'] = self.object.discussions.select_related(
            'author'
        ).order_by('-created_at')[:10]
        
        # Get announcements
        context['announcements'] = self.object.announcements.filter(
            is_pinned=False
        ).order_by('-created_at')[:5]
        
        # Get pinned announcements
        context['pinned_announcements'] = self.object.announcements.filter(
            is_pinned=True
        ).order_by('-created_at')
        
        # Check if user is a member
        if self.request.user.is_authenticated:
            context['is_member'] = self.object.members.filter(pk=self.request.user.pk).exists()
        else:
            context['is_member'] = False
        
        # Get member count
        context['member_count'] = self.object.member_count
        context['activity_count'] = self.object.activity_count
        context['last_activity'] = self.object.last_activity
        
        return context


@login_required
@require_http_methods(["POST"])
def group_join(request, slug):
    """Join or leave a community group."""
    group = get_object_or_404(CommunityGroup, slug=slug, is_public=True)
    
    if group.members.filter(pk=request.user.pk).exists():
        # Leave group
        group.members.remove(request.user)
        action = 'left'
        messages.success(request, _('You have left the group.'))
    else:
        # Join group
        group.members.add(request.user)
        action = 'joined'
        messages.success(request, _('You have joined the group.'))
    
    if request.headers.get('HX-Request'):
        return render(request, 'community/partials/group_join_button.html', {
            'group': group,
            'is_member': action == 'joined'
        })
    
    return redirect('community:group_detail', slug=slug)


class GroupDiscussionListView(ListView):
    """List discussions within a group."""
    model = GroupDiscussion
    template_name = 'community/groups/discussion.html'
    context_object_name = 'discussions'
    paginate_by = 20
    
    def get_queryset(self):
        group = get_object_or_404(CommunityGroup, slug=self.kwargs['slug'], is_public=True)
        return GroupDiscussion.objects.filter(group=group).select_related(
            'author', 'group'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(
            CommunityGroup,
            slug=self.kwargs['slug'],
            is_public=True
        )
        
        # Check if user is a member
        if self.request.user.is_authenticated:
            context['is_member'] = context['group'].members.filter(
                pk=self.request.user.pk
            ).exists()
        else:
            context['is_member'] = False
        
        return context
