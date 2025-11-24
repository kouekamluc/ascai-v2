"""
Views for students app.
"""
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from apps.universities.models import University, SavedUniversity
from apps.scholarships.models import Scholarship, SavedScholarship
from apps.downloads.models import Document


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
    """PDF resources and useful links."""
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
        return context

