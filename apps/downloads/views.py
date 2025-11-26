"""
Views for downloads app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.http import FileResponse, Http404, JsonResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict
from .models import Document


class DownloadListView(ListView):
    """List view for downloadable documents grouped by category."""
    model = Document
    template_name = 'downloads/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Document.objects.filter(is_active=True)
        
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group documents by category
        documents = context['documents']
        grouped_documents = OrderedDict()
        
        for doc in documents:
            category_key = doc.category
            category_display = doc.get_category_display()
            
            if category_key not in grouped_documents:
                grouped_documents[category_key] = {
                    'name': category_display,
                    'documents': []
                }
            grouped_documents[category_key]['documents'].append(doc)
        
        context['grouped_documents'] = grouped_documents
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'downloads/partials/document_list_partial.html'
        return super().get_template_names()
    
    def render_to_response(self, context, **response_kwargs):
        # Ensure grouped_documents is available for partial templates too
        if self.request.headers.get('HX-Request'):
            documents = context.get('documents', [])
            grouped_documents = OrderedDict()
            
            for doc in documents:
                category_key = doc.category
                category_display = doc.get_category_display()
                
                if category_key not in grouped_documents:
                    grouped_documents[category_key] = {
                        'name': category_display,
                        'documents': []
                    }
                grouped_documents[category_key]['documents'].append(doc)
            
            context['grouped_documents'] = grouped_documents
        
        return super().render_to_response(context, **response_kwargs)


def document_download(request, pk):
    """Download document view."""
    document = get_object_or_404(Document, pk=pk, is_active=True)
    
    # Increment download count (if not already incremented by HTMX)
    if not request.headers.get('HX-Request'):
        document.increment_download_count()
    
    try:
        response = FileResponse(document.file.open(), content_type='application/octet-stream')
        filename = document.file.name.split('/')[-1]  # Get just the filename
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        raise Http404("Document file not found.")


def increment_download_count(request, pk):
    """HTMX endpoint to increment download count and return updated count."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    document = get_object_or_404(Document, pk=pk, is_active=True)
    document.increment_download_count()
    
    return render(request, 'downloads/partials/download_count.html', {
        'document': document
    })

