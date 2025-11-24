"""
Views for students app.
"""
from django.views.generic import TemplateView


class StudentsIndexView(TemplateView):
    """Main students page."""
    template_name = 'students/index.html'


class LivingGuideView(TemplateView):
    """Guide for living in Lazio."""
    template_name = 'students/living_guide.html'


class UniversitiesListView(TemplateView):
    """List of universities in Lazio."""
    template_name = 'students/universities_list.html'


class EnrollmentProcessView(TemplateView):
    """Enrollment process guide."""
    template_name = 'students/enrollment_process.html'


class OrientationView(TemplateView):
    """Orientation advice."""
    template_name = 'students/orientation.html'

