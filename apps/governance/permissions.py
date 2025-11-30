"""
Custom permissions for governance app.
"""
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def create_governance_permissions(sender, **kwargs):
    """
    Create custom permissions for governance features.
    """
    from apps.governance import models
    
    # Get content types
    member_ct = ContentType.objects.get_for_model(models.Member)
    executive_board_ct = ContentType.objects.get_for_model(models.ExecutiveBoard)
    assembly_ct = ContentType.objects.get_for_model(models.GeneralAssembly)
    financial_ct = ContentType.objects.get_for_model(models.FinancialTransaction)
    election_ct = ContentType.objects.get_for_model(models.Election)
    sanction_ct = ContentType.objects.get_for_model(models.DisciplinarySanction)
    
    # Define permissions
    permissions = [
        # Membership permissions
        ('view_member', 'Can view member directory', member_ct),
        ('manage_member', 'Can manage members', member_ct),
        
        # Executive Board permissions
        ('manage_executive_board', 'Can manage executive board', executive_board_ct),
        ('view_executive_board', 'Can view executive board', executive_board_ct),
        
        # General Assembly permissions
        ('manage_assembly', 'Can manage general assemblies', assembly_ct),
        ('view_assembly', 'Can view general assemblies', assembly_ct),
        
        # Financial permissions
        ('manage_finances', 'Can manage finances', financial_ct),
        ('view_finances', 'Can view financial information', financial_ct),
        ('approve_expense', 'Can approve expenses (3-signature requirement)', financial_ct),
        
        # Electoral permissions
        ('manage_elections', 'Can manage elections', election_ct),
        ('view_elections', 'Can view elections', election_ct),
        
        # Disciplinary permissions
        ('apply_sanctions', 'Can apply disciplinary sanctions', sanction_ct),
        ('view_sanctions', 'Can view disciplinary sanctions', sanction_ct),
    ]
    
    # Create permissions
    for codename, name, content_type in permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    """
    Create permissions after migrations.
    """
    if sender.name == 'governance':
        create_governance_permissions(sender, **kwargs)

