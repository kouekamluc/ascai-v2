"""
Models for mentorship app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

User = get_user_model()


class MentorProfile(models.Model):
    """Mentor profile model."""
    AVAILABILITY_CHOICES = [
        ('available', _('Available')),
        ('busy', _('Busy')),
        ('unavailable', _('Unavailable')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mentor_profile',
        verbose_name=_('User')
    )
    specialization = models.CharField(max_length=200, verbose_name=_('Specialization'))
    years_experience = models.PositiveIntegerField(verbose_name=_('Years of Experience'))
    bio = models.TextField(verbose_name=_('Bio'))
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available',
        verbose_name=_('Availability Status')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Approved'),
        help_text=_('Must be approved by admin to be visible.')
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Rating')
    )
    students_helped = models.PositiveIntegerField(default=0, verbose_name=_('Students Helped'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Mentor Profile')
        verbose_name_plural = _('Mentor Profiles')
        ordering = ['-rating', '-students_helped']
    
    def __str__(self):
        return f"Mentor: {self.user.username}"


class MentorshipRequest(models.Model):
    """Mentorship request model."""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentorship_requests',
        verbose_name=_('Student')
    )
    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name=_('Mentor')
    )
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Mentorship Request')
        verbose_name_plural = _('Mentorship Requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Request from {self.student.username} to {self.mentor.user.username}"


class MentorshipMessage(models.Model):
    """Mentorship message model."""
    request = models.ForeignKey(
        MentorshipRequest,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Request')
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentorship_messages_sent',
        verbose_name=_('Sender')
    )
    content = models.TextField(verbose_name=_('Content'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Mentorship Message')
        verbose_name_plural = _('Mentorship Messages')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username}"

















