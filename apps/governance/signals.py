"""
Signals for governance app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import (
    Member, MembershipStatus, ExecutivePosition, BoardMeeting,
    GeneralAssembly, MembershipDues, FinancialTransaction, ExpenseApproval,
    BoardOfAuditors, AuditorMember
)


@receiver(post_save, sender=Member)
def create_initial_membership_status(sender, instance, created, **kwargs):
    """
    Create initial membership status when member is created.
    """
    if created:
        MembershipStatus.objects.create(
            member=instance,
            status='active',
            effective_date=timezone.now().date()
        )


@receiver(post_save, sender=ExecutivePosition)
def track_executive_position_changes(sender, instance, created, **kwargs):
    """
    Track executive position changes and enforce term limits.
    """
    if not created and instance.status == 'resigned':
        # Update end_date when position is resigned
        if not instance.end_date:
            instance.end_date = timezone.now().date()
            instance.save(update_fields=['end_date'])


@receiver(post_save, sender=GeneralAssembly)
def check_assembly_notice_period(sender, instance, created, **kwargs):
    """
    Validate that assembly notice period is at least 10 days (Article 4).
    This is a warning signal - actual validation should be in forms/views.
    """
    if instance.convocation_date and instance.date:
        notice_days = (instance.date.date() - instance.convocation_date).days
        if notice_days < 10:
            # Log warning - actual enforcement should be in forms
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"General Assembly {instance} has notice period of {notice_days} days "
                f"(minimum 10 days required per Article 4)"
            )


@receiver(post_save, sender=MembershipDues)
def update_membership_status_on_payment(sender, instance, **kwargs):
    """
    Update membership status when dues are paid.
    """
    if instance.status == 'paid' and instance.payment_date:
        # Update last payment date in membership status
        latest_status = instance.member.status_history.first()
        if latest_status:
            latest_status.last_payment_date = instance.payment_date
            latest_status.save(update_fields=['last_payment_date'])
        
        # Mark member as active if they pay dues
        if not instance.member.is_active_member:
            instance.member.is_active_member = True
            instance.member.save(update_fields=['is_active_member'])


@receiver(post_save, sender=MembershipDues)
def check_membership_expiration(sender, instance, **kwargs):
    """
    Check if membership should expire (3 months after due date without payment).
    """
    if instance.status != 'paid' and instance.due_date:
        three_months_later = instance.due_date + timedelta(days=90)
        if timezone.now().date() > three_months_later:
            # Membership should be lost (Article 29)
            if instance.member.is_active_member:
                instance.member.is_active_member = False
                instance.member.save(update_fields=['is_active_member'])
                
                # Create status change
                MembershipStatus.objects.create(
                    member=instance.member,
                    status='inactive',
                    effective_date=three_months_later,
                    reason='Non-payment of annual dues (3 months after due date)'
                )


@receiver(post_save, sender=FinancialTransaction)
def create_expense_approvals(sender, instance, created, **kwargs):
    """
    Create expense approval records when expense transaction is created.
    Requires 3 signatures: President, Treasurer, Statutory Auditor (Article 44).
    """
    if created and instance.transaction_type == 'expense' and instance.requires_approval:
        # Get current executive board positions
        from .models import ExecutiveBoard
        current_board = ExecutiveBoard.objects.filter(status='active').first()
        
        if current_board:
            # Get required signers
            president = ExecutivePosition.objects.filter(
                board=current_board,
                position='president',
                status='active'
            ).first()
            
            treasurer = ExecutivePosition.objects.filter(
                board=current_board,
                position='treasurer',
                status='active'
            ).first()
            
            auditor = ExecutivePosition.objects.filter(
                board=current_board,
                position='statutory_auditor',
                status='active'
            ).first()
            
            # Create approval records for each required signer
            if president and president.user:
                ExpenseApproval.objects.get_or_create(
                    transaction=instance,
                    signer=president.user,
                    defaults={'status': 'pending'}
                )
            
            if treasurer and treasurer.user:
                ExpenseApproval.objects.get_or_create(
                    transaction=instance,
                    signer=treasurer.user,
                    defaults={'status': 'pending'}
                )
            
            if auditor and auditor.user:
                ExpenseApproval.objects.get_or_create(
                    transaction=instance,
                    signer=auditor.user,
                    defaults={'status': 'pending'}
                )


@receiver(post_save, sender=ExpenseApproval)
def check_expense_approval_complete(sender, instance, **kwargs):
    """
    Check if expense has all 3 required approvals and update transaction status.
    """
    if instance.status == 'signed':
        transaction = instance.transaction
        
        # Count signed approvals
        signed_approvals = transaction.approvals.filter(status='signed').count()
        
        # If all 3 required approvals are signed, mark transaction as approved
        if signed_approvals >= 3:
            if transaction.status != 'approved':
                transaction.status = 'approved'
                transaction.save(update_fields=['status'])


@receiver(post_save, sender=BoardOfAuditors)
def auto_include_founding_members_and_former_presidents(sender, instance, created, **kwargs):
    """
    Automatically include founding members and former presidents in Board of Auditors (Article 8).
    This is a backup signal in case the save() method doesn't run.
    """
    if created:
        # Auto-add founding members
        founding_members = Member.objects.filter(is_founding_member=True)
        for member in founding_members:
            AuditorMember.objects.get_or_create(
                board=instance,
                user=member.user,
                defaults={
                    'is_founding_member': True,
                }
            )
        
        # Auto-add former presidents (from ExecutivePosition history)
        former_presidents = ExecutivePosition.objects.filter(
            position='president',
            status__in=['resigned', 'replaced'],
            end_date__isnull=False
        ).select_related('user').distinct('user')
        
        for position in former_presidents:
            if position.user:
                AuditorMember.objects.get_or_create(
                    board=instance,
                    user=position.user,
                    defaults={
                        'is_former_president': True,
                    }
                )



