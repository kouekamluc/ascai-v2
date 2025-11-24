"""
Views for community/forum app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Count, Q, F
from django.utils.translation import gettext_lazy as _
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
            post_count=Count('posts')
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
        context['posts'] = self.object.posts.select_related('author').order_by('created_at')
        
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
        thread.upvotes_count = max(0, thread.upvotes_count - 1)
        has_upvoted = False
    else:
        thread.upvotes_count += 1
        has_upvoted = True
    
    thread.save()
    
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
        post.upvotes_count = max(0, post.upvotes_count - 1)
        has_upvoted = False
    else:
        post.upvotes_count += 1
        has_upvoted = True
    
    post.save()
    
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
    """Delete thread (Admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    thread = get_object_or_404(ForumThread, slug=slug)
    thread.delete()
    
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
    """Delete post (Admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': _('Permission denied.')}, status=403)
    
    post = get_object_or_404(ForumPost, id=post_id)
    thread = post.thread
    post.delete()
    
    if request.headers.get('HX-Request'):
        # Return empty string to remove the element
        from django.http import HttpResponse
        return HttpResponse('')
    
    return redirect('community:thread_detail', slug=thread.slug)

