"""
Models for mentorship app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

User = get_user_model()


class MentorSpecialization(models.Model):
    """Mentor specialization categories."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class name'),
        verbose_name=_('Icon')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    
    class Meta:
        verbose_name = _('Mentor Specialization')
        verbose_name_plural = _('Mentor Specializations')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


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
    specializations = models.ManyToManyField(
        MentorSpecialization,
        blank=True,
        related_name='mentors',
        verbose_name=_('Specializations'),
        help_text=_('Select one or more specializations.')
    )
    years_experience = models.PositiveIntegerField(verbose_name=_('Years of Experience'))
    bio = models.TextField(verbose_name=_('Bio'))
    profile_image = models.ImageField(
        upload_to='mentors/profiles/',
        blank=True,
        null=True,
        verbose_name=_('Profile Image')
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available',
        verbose_name=_('Availability Status')
    )
    availability_calendar = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Availability Calendar'),
        help_text=_('JSON structure for availability schedule (e.g., {"monday": ["09:00-12:00"], "tuesday": ["14:00-17:00"]})')
    )
    response_time = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Average Response Time'),
        help_text=_('e.g., "Within 24 hours", "Within 2-3 days"')
    )
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Success Rate (%)'),
        help_text=_('Percentage of successful mentorship sessions')
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
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Mentor Profile')
        verbose_name_plural = _('Mentor Profiles')
        ordering = ['-rating', '-students_helped']
    
    def __str__(self):
        return f"Mentor: {self.user.username}"
    
    def update_rating(self):
        """Update average rating from all ratings."""
        from django.db.models import Avg
        avg_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            self.rating = round(avg_rating, 2)
        else:
            self.rating = 0.00
        self.save(update_fields=['rating'])
    
    def increment_students_helped(self):
        """Increment students helped count."""
        self.students_helped += 1
        self.save(update_fields=['students_helped'])
    
    def calculate_success_rate(self):
        """Calculate success rate from completed requests."""
        total_completed = self.requests.filter(status='completed').count()
        total_accepted = self.requests.filter(status__in=['accepted', 'completed']).count()
        if total_accepted > 0:
            self.success_rate = round((total_completed / total_accepted) * 100, 2)
        else:
            self.success_rate = 0.00
        self.save(update_fields=['success_rate'])


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
    
    def can_be_completed(self):
        """Check if request can be marked as completed."""
        return self.status == 'accepted'
    
    def has_rating(self):
        """Check if this request has been rated."""
        try:
            # Check if related rating object exists
            return hasattr(self, 'rating') and self.rating is not None
        except Exception:
            return False


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


class MentorRating(models.Model):
    """Rating given by student to mentor after mentorship completion."""
    request = models.OneToOneField(
        MentorshipRequest,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name=_('Request')
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentor_ratings_given',
        verbose_name=_('Student')
    )
    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('Mentor')
    )
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Rating')
    )
    comment = models.TextField(blank=True, verbose_name=_('Comment'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Mentor Rating')
        verbose_name_plural = _('Mentor Ratings')
        ordering = ['-created_at']
        unique_together = ['request', 'student']
    
    def __str__(self):
        return f"Rating {self.rating}/5 for {self.mentor.user.username} by {self.student.username}"


class MentorshipSession(models.Model):
    """Scheduled mentorship session model."""
    request = models.ForeignKey(
        MentorshipRequest,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('Request')
    )
    scheduled_at = models.DateTimeField(
        verbose_name=_('Scheduled At')
    )
    duration = models.DurationField(
        verbose_name=_('Duration'),
        help_text=_('Session duration (e.g., 1:00:00 for 1 hour)')
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Location'),
        help_text=_('Physical location or video call link')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Session notes or agenda')
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_('Completed')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Session Rating'),
        help_text=_('Rating given after session completion')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Mentorship Session')
        verbose_name_plural = _('Mentorship Sessions')
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"Session for {self.request.student.username} with {self.request.mentor.user.username} on {self.scheduled_at}"












