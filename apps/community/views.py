"""
Views for community/forum app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Count, Q, F
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import ForumCategory, ForumThread, ForumPost, ThreadUpvote, PostUpvote
from .forms import ThreadForm, PostForm


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
        # Increment views count
        ForumThread.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        # Refresh from database to get updated count
        obj.refresh_from_db()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Order posts: solutions first, then by creation date
        context['posts'] = self.object.posts.select_related('author').order_by('-is_solution', 'created_at')
        
        # Check if user has upvoted
        if self.request.user.is_authenticated:
            context['has_upvoted_thread'] = ThreadUpvote.objects.filter(
                thread=self.object,
                user=self.request.user
            ).exists()
            context['upvoted_post_ids'] = list(
                PostUpvote.objects.filter(
                    user=self.request.user,
                    post__thread=self.object
                ).values_list('post_id', flat=True)
            )
        else:
            context['has_upvoted_thread'] = False
            context['upvoted_post_ids'] = []
        
        # Pass user to context for moderation checks
        context['user'] = self.request.user
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle post creation via HTMX."""
        self.object = self.get_object()
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
            context = self.get_context_data(**kwargs)
            context['post'] = post
            # Get upvoted post IDs for the new post
            if request.user.is_authenticated:
                upvoted_post_ids = list(
                    PostUpvote.objects.filter(
                        user=request.user,
                        post__thread=self.object
                    ).values_list('post_id', flat=True)
                )
            else:
                upvoted_post_ids = []
            return render(request, 'community/partials/post_item.html', {
                'post': post, 
                'user': request.user,
                'upvoted_post_ids': upvoted_post_ids
            })
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
        # Return empty string to remove the element
        from django.http import HttpResponse
        return HttpResponse('')
    
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
    post.refresh_from_db()
    
    if request.headers.get('HX-Request'):
        # Get upvoted post IDs
        if request.user.is_authenticated:
            upvoted_post_ids = list(
                PostUpvote.objects.filter(
                    user=request.user,
                    post__thread=thread
                ).values_list('post_id', flat=True)
            )
        else:
            upvoted_post_ids = []
        
        return render(request, 'community/partials/post_item.html', {
            'post': post,
            'user': request.user,
            'upvoted_post_ids': upvoted_post_ids,
            'thread': thread
        })
    
    return JsonResponse({'is_solution': post.is_solution})

