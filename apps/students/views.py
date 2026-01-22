"""
Views for students app.
"""
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from apps.universities.models import University, SavedUniversity
from apps.scholarships.models import Scholarship, SavedScholarship
from apps.downloads.models import Document
from .models import (
    ResourceCategory, ResourceLink,
    StudentGuideSection, StudentGuideStep, StudentGuideProgress
)


class StudentsIndexView(TemplateView):
    """Main students page - Studying in Lazio Complete Guide."""
    template_name = 'students/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get counts for dashboard
        context['universities_count'] = University.objects.count()
        context['scholarships_count'] = Scholarship.objects.filter(status='active').count()
        context['documents_count'] = Document.objects.filter(is_active=True).count()
        return context


class LivingGuideView(TemplateView):
    """Guide for living in Lazio."""
    template_name = 'students/living_guide.html'


class UniversitiesListView(ListView):
    """List of universities in Lazio with HTMX filtering."""
    model = University
    template_name = 'students/universities_list.html'
    context_object_name = 'universities'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = University.objects.all()
        
        # HTMX filtering
        city = self.request.GET.get('city')
        degree_type = self.request.GET.get('degree_type')
        field = self.request.GET.get('field')
        language = self.request.GET.get('language')
        search = self.request.GET.get('search')
        
        if city:
            queryset = queryset.filter(city=city)
        
        if degree_type:
            queryset = queryset.filter(degree_types__contains=[degree_type])
        
        if field:
            queryset = queryset.filter(fields_of_study__contains=[field])
        
        if language:
            queryset = queryset.filter(languages__contains=[language])
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_template_names(self):
        """Return different template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return 'students/partials/university_list_partial.html'
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter values to context
        context['filter_city'] = self.request.GET.get('city', '')
        context['filter_degree_type'] = self.request.GET.get('degree_type', '')
        context['filter_field'] = self.request.GET.get('field', '')
        context['filter_language'] = self.request.GET.get('language', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Get saved universities for logged-in users
        if self.request.user.is_authenticated:
            context['saved_university_ids'] = list(
                SavedUniversity.objects.filter(user=self.request.user).values_list('university_id', flat=True)
            )
        else:
            context['saved_university_ids'] = []
        
        return context


class StudyProgramsView(TemplateView):
    """Study programs overview (Bachelor, Master, PhD)."""
    template_name = 'students/study_programs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.universities.models import UniversityProgram
        
        # Get programs by degree type
        context['bachelor_programs'] = UniversityProgram.objects.filter(degree_type='bachelor')[:10]
        context['master_programs'] = UniversityProgram.objects.filter(degree_type='master')[:10]
        context['phd_programs'] = UniversityProgram.objects.filter(degree_type='phd')[:10]
        context['total_bachelor'] = UniversityProgram.objects.filter(degree_type='bachelor').count()
        context['total_master'] = UniversityProgram.objects.filter(degree_type='master').count()
        context['total_phd'] = UniversityProgram.objects.filter(degree_type='phd').count()
        
        return context


class ErasmusExchangeView(TemplateView):
    """Erasmus and Exchange programs information."""
    template_name = 'students/erasmus_exchange.html'


class ScholarshipsListView(ListView):
    """List of scholarships available to students with HTMX filtering."""
    model = Scholarship
    template_name = 'students/scholarships_list.html'
    context_object_name = 'scholarships'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Scholarship.objects.filter(status='active')
        
        is_disco = self.request.GET.get('is_disco_lazio')
        search = self.request.GET.get('search')
        
        if is_disco == 'true':
            queryset = queryset.filter(is_disco_lazio=True)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(provider__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'students/partials/scholarship_list_partial.html'
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['saved_scholarship_ids'] = list(
                SavedScholarship.objects.filter(user=self.request.user).values_list('scholarship_id', flat=True)
            )
        else:
            context['saved_scholarship_ids'] = []
        
        return context


class EnrollmentProcessView(TemplateView):
    """Enrollment process guide."""
    template_name = 'students/enrollment_process.html'


class OrientationView(TemplateView):
    """Orientation advice."""
    template_name = 'students/orientation.html'


class ResourcesView(ListView):
    """Enhanced PDF resources and useful links with categories and external links."""
    model = Document
    template_name = 'students/resources.html'
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
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return 'students/partials/resources_list_partial.html'
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Get resource categories
        context['resource_categories'] = ResourceCategory.objects.filter(is_active=True).order_by('order', 'name')
        
        # Get featured resources (documents with high download count)
        context['featured_documents'] = Document.objects.filter(
            is_active=True
        ).annotate(
            download_count_annotated=Count('download_count')
        ).order_by('-download_count')[:6]
        
        # Get popular resources (by download count)
        context['popular_documents'] = Document.objects.filter(
            is_active=True
        ).order_by('-download_count')[:10]
        
        # Get external resource links
        context['resource_links'] = ResourceLink.objects.all().order_by('order', 'title')
        context['featured_links'] = ResourceLink.objects.filter(is_featured=True).order_by('order', 'title')
        
        # Get recent resources
        context['recent_documents'] = Document.objects.filter(is_active=True).order_by('-uploaded_at')[:5]
        
        return context


class ResourceDetailView(DetailView):
    """Individual resource detail page."""
    model = Document
    template_name = 'students/resource_detail.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        return Document.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related documents (same category)
        context['related_documents'] = Document.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(pk=self.object.pk)[:5]
        return context


class NewStudentGuideView(TemplateView):
    """Main new student guide page with progress tracker."""
    template_name = 'students/new_student_guide.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all guide sections
        sections = StudentGuideSection.objects.filter(is_active=True).order_by('order', 'title')
        context['sections'] = sections
        
        # Get user progress if logged in
        if self.request.user.is_authenticated:
            progress_dict = {}
            for section in sections:
                progress, created = StudentGuideProgress.objects.get_or_create(
                    user=self.request.user,
                    section=section
                )
                progress_dict[section.id] = {
                    'progress': progress,
                    'completion_percentage': progress.get_completion_percentage(),
                    'is_completed': progress.is_completed
                }
            context['user_progress'] = progress_dict
            
            # Calculate overall progress
            total_sections = sections.count()
            completed_sections = sum(1 for p in progress_dict.values() if p['is_completed'])
            context['overall_progress'] = int((completed_sections / total_sections * 100)) if total_sections > 0 else 0
        else:
            context['user_progress'] = {}
            context['overall_progress'] = 0
        
        return context


class GuideSectionDetailView(DetailView):
    """Individual guide section detail page."""
    model = StudentGuideSection
    template_name = 'students/guide_section_detail.html'
    context_object_name = 'section'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return StudentGuideSection.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all steps for this section
        context['steps'] = self.object.steps.all().order_by('order', 'title')
        
        # Get user progress if logged in
        if self.request.user.is_authenticated:
            progress, created = StudentGuideProgress.objects.get_or_create(
                user=self.request.user,
                section=self.object
            )
            context['user_progress'] = progress
            context['completion_percentage'] = progress.get_completion_percentage()
            context['completed_step_ids'] = list(progress.completed_steps.values_list('id', flat=True))
        else:
            context['user_progress'] = None
            context['completion_percentage'] = 0
            context['completed_step_ids'] = []
        
        # Get previous and next sections
        all_sections = StudentGuideSection.objects.filter(is_active=True).order_by('order', 'title')
        section_list = list(all_sections)
        try:
            current_index = section_list.index(self.object)
            context['previous_section'] = section_list[current_index - 1] if current_index > 0 else None
            context['next_section'] = section_list[current_index + 1] if current_index < len(section_list) - 1 else None
        except ValueError:
            context['previous_section'] = None
            context['next_section'] = None
        
        return context


class GuideStepDetailView(DetailView):
    """Individual guide step detail page."""
    model = StudentGuideStep
    template_name = 'students/guide_step_detail.html'
    context_object_name = 'step'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all steps in the section for navigation
        context['all_steps'] = self.object.section.steps.all().order_by('order', 'title')
        step_list = list(context['all_steps'])
        try:
            current_index = step_list.index(self.object)
            context['previous_step'] = step_list[current_index - 1] if current_index > 0 else None
            context['next_step'] = step_list[current_index + 1] if current_index < len(step_list) - 1 else None
        except ValueError:
            context['previous_step'] = None
            context['next_step'] = None
        
        # Get user progress if logged in
        if self.request.user.is_authenticated:
            progress, created = StudentGuideProgress.objects.get_or_create(
                user=self.request.user,
                section=self.object.section
            )
            context['user_progress'] = progress
            context['is_step_completed'] = progress.completed_steps.filter(pk=self.object.pk).exists()
        else:
            context['user_progress'] = None
            context['is_step_completed'] = False
        
        return context


@login_required
@require_http_methods(["POST"])
def save_guide_progress(request, step_id):
    """Save user progress for a guide step (AJAX endpoint)."""
    step = get_object_or_404(StudentGuideStep, pk=step_id)
    
    # Get or create progress for this section
    progress, created = StudentGuideProgress.objects.get_or_create(
        user=request.user,
        section=step.section
    )
    
    # Add step to completed steps
    progress.completed_steps.add(step)
    
    # Check if all steps are completed
    total_steps = step.section.steps.count()
    completed_count = progress.completed_steps.count()
    
    if completed_count >= total_steps:
        progress.is_completed = True
        progress.save()
    
    return JsonResponse({
        'success': True,
        'completion_percentage': progress.get_completion_percentage(),
        'is_section_completed': progress.is_completed
    })

