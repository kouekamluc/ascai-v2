"""
Models for dashboard app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
import uuid

User = get_user_model()


class SupportTicket(models.Model):
    """
    Support ticket model for user-admin communication.
    """
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('pending', _('Pending')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name=_('User')
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name=_('Subject')
    )
    
    message = models.TextField(
        verbose_name=_('Message')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_('Status')
    )
    
    admin_response = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Admin Response')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolved At')
    )
    
    class Meta:
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class TicketReply(models.Model):
    """
    Reply model for support tickets to enable conversation threading.
    """
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name=_('Ticket')
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_replies',
        verbose_name=_('Author')
    )
    
    message = models.TextField(
        verbose_name=_('Message')
    )
    
    is_admin_reply = models.BooleanField(
        default=False,
        verbose_name=_('Admin Reply'),
        help_text=_('Whether this reply is from an admin.')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Ticket Reply')
        verbose_name_plural = _('Ticket Replies')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.ticket.subject} by {self.author.username}"


class CommunityGroup(models.Model):
    """
    Community group model for internal groups.
    """
    CATEGORY_CHOICES = [
        ('universities', _('Lazio Universities Group')),
        ('students', _('Rome Cameroonian Students')),
        ('professionals', _('Professionals in Lazio')),
        ('new_students', _('New Students Support Group')),
        ('women', _('Women in the Diaspora Group')),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name')
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        verbose_name=_('Description')
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Category')
    )
    
    members = models.ManyToManyField(
        User,
        related_name='community_groups',
        blank=True,
        verbose_name=_('Members')
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Is Public'),
        help_text=_('Public groups are visible to all authenticated users.')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups',
        verbose_name=_('Created By')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Community Group')
        verbose_name_plural = _('Community Groups')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('dashboard:group_detail', kwargs={'slug': self.slug})


class GroupDiscussion(models.Model):
    """
    Discussion thread within a community group.
    """
    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='discussions',
        verbose_name=_('Group')
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_discussions',
        verbose_name=_('Author')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    content = models.TextField(
        verbose_name=_('Content')
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
        verbose_name = _('Group Discussion')
        verbose_name_plural = _('Group Discussions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"


class GroupAnnouncement(models.Model):
    """
    Announcement within a community group.
    """
    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_('Group')
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_announcements',
        verbose_name=_('Author')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    content = models.TextField(
        verbose_name=_('Content')
    )
    
    is_pinned = models.BooleanField(
        default=False,
        verbose_name=_('Pinned')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Group Announcement')
        verbose_name_plural = _('Group Announcements')
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"


class GroupFile(models.Model):
    """
    File uploaded to a community group.
    """
    group = models.ForeignKey(
        CommunityGroup,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Group')
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_group_files',
        verbose_name=_('Uploaded By')
    )
    
    file = models.FileField(
        upload_to='group_files/%Y/%m/',
        verbose_name=_('File')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )
    
    class Meta:
        verbose_name = _('Group File')
        verbose_name_plural = _('Group Files')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"


class StoryImage(models.Model):
    """
    Image for user story submissions.
    """
    image = models.ImageField(
        upload_to='story_images/%Y/%m/',
        verbose_name=_('Image')
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Caption')
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )
    
    class Meta:
        verbose_name = _('Story Image')
        verbose_name_plural = _('Story Images')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.caption or f"Image {self.id}"


class UserStorySubmission(models.Model):
    """
    User-submitted diaspora story for review and publication.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('under_review', _('Under Review')),
        ('published', _('Published')),
        ('declined', _('Declined')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='story_submissions',
        verbose_name=_('User')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    
    story = models.TextField(
        verbose_name=_('Story')
    )
    
    images = models.ManyToManyField(
        StoryImage,
        blank=True,
        related_name='story_submissions',
        verbose_name=_('Images')
    )
    
    documents = models.FileField(
        upload_to='story_documents/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Supporting Documents')
    )
    
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name=_('Anonymous'),
        help_text=_('If checked, the story will be published without your name.')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Admin Notes')
    )
    
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Submitted At')
    )
    
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed At')
    )
    
    class Meta:
        verbose_name = _('Story Submission')
        verbose_name_plural = _('Story Submissions')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class EventRegistration(models.Model):
    """
    Event registration model with QR code support.
    """
    event = models.ForeignKey(
        'diaspora.Event',
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name=_('Event')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        verbose_name=_('User')
    )
    
    registration_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Registration Code'),
        help_text=_('Unique code for QR code generation.')
    )
    
    attended = models.BooleanField(
        default=False,
        verbose_name=_('Attended')
    )
    
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Registered At')
    )
    
    class Meta:
        verbose_name = _('Event Registration')
        verbose_name_plural = _('Event Registrations')
        unique_together = ['event', 'user']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.registration_code:
            self.registration_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class SavedDocument(models.Model):
    """
    User's saved documents from the reserved downloads section.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_documents',
        verbose_name=_('User')
    )
    
    document = models.ForeignKey(
        'downloads.Document',
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        verbose_name=_('Document')
    )
    
    saved_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Saved At')
    )
    
    class Meta:
        verbose_name = _('Saved Document')
        verbose_name_plural = _('Saved Documents')
        unique_together = ['user', 'document']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.document.title}"


class StudentQuestion(models.Model):
    """
    Questions submitted by new students for assistance.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_questions',
        verbose_name=_('User')
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name=_('Subject')
    )
    
    question = models.TextField(
        verbose_name=_('Question')
    )
    
    category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Category'),
        help_text=_('e.g., Residence Permit, University Enrollment, etc.')
    )
    
    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_('Resolved')
    )
    
    admin_response = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Admin Response')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolved At')
    )
    
    class Meta:
        verbose_name = _('Student Question')
        verbose_name_plural = _('Student Questions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class OrientationSession(models.Model):
    """
    Orientation session booking for new students.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orientation_sessions',
        verbose_name=_('User')
    )
    
    preferred_date = models.DateField(
        verbose_name=_('Preferred Date')
    )
    
    preferred_time = models.TimeField(
        verbose_name=_('Preferred Time')
    )
    
    topics = models.TextField(
        verbose_name=_('Topics of Interest'),
        help_text=_('What topics would you like to discuss?')
    )
    
    is_confirmed = models.BooleanField(
        default=False,
        verbose_name=_('Confirmed')
    )
    
    confirmed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Confirmed Date & Time')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Orientation Session')
        verbose_name_plural = _('Orientation Sessions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.preferred_date}"
