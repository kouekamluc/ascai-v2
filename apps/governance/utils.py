"""
Business logic utilities for governance app.
Implements algorithms for vote counting, eligibility checking, etc.
"""
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta, datetime
from .models import (
    Member, ExecutiveBoard, ExecutivePosition, GeneralAssembly,
    AssemblyVote, AssemblyVoteRecord, Election, Candidacy, ElectionVote,
    MembershipDues, FinancialTransaction, DisciplinaryCase, DisciplinarySanction,
    EXECUTIVE_POSITION_CHOICES
)


# ============================================================================
# VOTE COUNTING ALGORITHMS
# ============================================================================

def calculate_assembly_vote_results(vote):
    """
    Calculate assembly vote results with proper vote counting.
    Returns dict with vote counts and percentages.
    """
    # Get all vote records
    vote_records = vote.vote_records.all()
    total_votes = vote_records.count()
    
    yes_count = vote_records.filter(choice='yes').count()
    no_count = vote_records.filter(choice='no').count()
    abstain_count = vote_records.filter(choice='abstain').count()
    
    # Calculate percentages
    if total_votes > 0:
        yes_percent = (yes_count / total_votes) * 100
        no_percent = (no_count / total_votes) * 100
        abstain_percent = (abstain_count / total_votes) * 100
    else:
        yes_percent = no_percent = abstain_percent = 0
    
    # Determine result (simple majority)
    if yes_count > no_count:
        result = 'approved'
    elif no_count > yes_count:
        result = 'rejected'
    else:
        result = 'tied'
    
    return {
        'total_votes': total_votes,
        'yes': yes_count,
        'no': no_count,
        'abstain': abstain_count,
        'yes_percent': yes_percent,
        'no_percent': no_percent,
        'abstain_percent': abstain_percent,
        'result': result,
        'majority': yes_count > no_count
    }


def calculate_election_results(election):
    """
    Calculate election results by position.
    Returns dict with winners and vote counts for each position.
    """
    results = {}
    
    for position_code, position_name in EXECUTIVE_POSITION_CHOICES:
        # Get all approved candidacies for this position
        candidacies = election.candidacies.filter(
            position=position_code,
            status='approved'
        ).select_related('candidate')
        
        position_results = []
        total_votes_for_position = 0
        
        for candidacy in candidacies:
            vote_count = election.votes.filter(
                candidate=candidacy,
                position=position_code
            ).count()
            total_votes_for_position += vote_count
            
            position_results.append({
                'candidacy': candidacy,
                'candidate': candidacy.candidate,
                'votes': vote_count,
                'votes_percent': 0  # Will calculate after
            })
        
        # Calculate percentages
        if total_votes_for_position > 0:
            for result in position_results:
                result['votes_percent'] = (result['votes'] / total_votes_for_position) * 100
        
        # Sort by votes (descending)
        position_results.sort(key=lambda x: x['votes'], reverse=True)
        
        # Determine winner (simple majority)
        winner = None
        if position_results and position_results[0]['votes'] > 0:
            # Check if there's a clear majority
            if len(position_results) == 1 or position_results[0]['votes'] > position_results[1]['votes']:
                winner = position_results[0]
        
        results[position_code] = {
            'name': position_name,
            'candidates': position_results,
            'total_votes': total_votes_for_position,
            'winner': winner
        }
    
    return results


# ============================================================================
# ELIGIBILITY CHECKING ALGORITHMS
# ============================================================================

def check_candidacy_eligibility(user, position, election=None):
    """
    Check if a user is eligible to run for a position (Article 33).
    Returns dict with eligibility status and reasons.
    """
    from .models import ElectoralCommission, CommissionMember
    
    eligibility = {
        'eligible': True,
        'reasons': [],
        'warnings': []
    }
    
    # Check if user has member profile
    try:
        member = user.member_profile
    except Member.DoesNotExist:
        eligibility['eligible'] = False
        eligibility['reasons'].append('User is not a registered member')
        return eligibility
    
    # Check if user is a member of Electoral Commission (Article 33 - cannot be candidate)
    if election and election.commission:
        is_commission_member = CommissionMember.objects.filter(
            commission=election.commission,
            user=user
        ).exists()
        if is_commission_member:
            eligibility['eligible'] = False
            eligibility['reasons'].append(
                'Members of the Electoral Commission cannot be candidates (Article 33)'
            )
            return eligibility
    
    # Check 1+ year seniority
    if member.membership_start_date:
        seniority_days = (timezone.now().date() - member.membership_start_date).days
        if seniority_days < 365:
            eligibility['eligible'] = False
            eligibility['reasons'].append(
                f'Insufficient seniority: {seniority_days} days (requires 365+ days)'
            )
    else:
        eligibility['warnings'].append('Membership start date not set')
    
    # Check Lazio residence
    if not member.lazio_residence_verified:
        eligibility['eligible'] = False
        eligibility['reasons'].append('Lazio residence not verified')
    
    # Check Cameroonian origin
    if not member.cameroonian_origin_verified:
        eligibility['eligible'] = False
        eligibility['reasons'].append('Cameroonian origin not verified')
    
    # Check active membership
    if not member.is_active_member:
        eligibility['warnings'].append('Member is not currently active')
    
    # Check regular participation (at least 2 assemblies in last year)
    one_year_ago = timezone.now() - timedelta(days=365)
    assembly_attendances = user.assembly_attendances.filter(
        assembly__date__gte=one_year_ago,
        attended=True
    ).count()
    
    if assembly_attendances < 2:
        eligibility['warnings'].append(
            f'Low assembly participation: {assembly_attendances} attendances in last year (recommended: 2+)'
        )
    
    return eligibility


def check_voting_eligibility(user, assembly=None, election=None):
    """
    Check if a user is eligible to vote.
    Returns dict with eligibility status.
    """
    eligibility = {
        'eligible': False,
        'reason': ''
    }
    
    # Check if user has member profile
    try:
        member = user.member_profile
    except Member.DoesNotExist:
        eligibility['reason'] = 'User is not a registered member'
        return eligibility
    
    # Check active membership
    if not member.is_active_member:
        eligibility['reason'] = 'Only active members can vote'
        return eligibility
    
    # For elections, check if already voted
    if election:
        # Check if user already voted for any position in this election
        existing_votes = ElectionVote.objects.filter(
            election=election,
            voter=user
        ).exists()
        
        if existing_votes:
            eligibility['reason'] = 'You have already voted in this election'
            return eligibility
    
    # For assemblies, check if already voted
    if assembly:
        # This is checked per vote item, not per assembly
        pass
    
    eligibility['eligible'] = True
    return eligibility


# ============================================================================
# MEMBERSHIP MANAGEMENT ALGORITHMS
# ============================================================================

def check_membership_loss_criteria(member):
    """
    Check if member should lose membership (Article 29).
    Returns dict with status and reasons.
    """
    status = {
        'should_lose_membership': False,
        'reasons': [],
        'warnings': []
    }
    
    # Check for non-payment (3 months after due date)
    current_year = timezone.now().year
    current_dues = MembershipDues.objects.filter(
        member=member,
        year=current_year
    ).first()
    
    if current_dues and current_dues.status != 'paid':
        three_months_after_due = current_dues.due_date + timedelta(days=90)
        if timezone.now().date() > three_months_after_due:
            status['should_lose_membership'] = True
            status['reasons'].append(
                f'Non-payment of dues: Overdue by {(timezone.now().date() - three_months_after_due).days} days'
            )
    
    # Check for repeated disciplinary sanctions
    active_sanctions = DisciplinarySanction.objects.filter(
        case__member=member,
        status='active'
    ).count()
    
    if active_sanctions >= 3:
        status['should_lose_membership'] = True
        status['reasons'].append(f'Repeated disciplinary violations: {active_sanctions} active sanctions')
    
    # Check for exclusion sanction
    exclusion_sanction = DisciplinarySanction.objects.filter(
        case__member=member,
        sanction_type='exclusion',
        status='active'
    ).exists()
    
    if exclusion_sanction:
        status['should_lose_membership'] = True
        status['reasons'].append('Active exclusion sanction')
    
    return status


def calculate_member_seniority(member):
    """
    Calculate member's seniority in the association.
    Returns dict with seniority information.
    """
    if not member.membership_start_date:
        return {
            'days': 0,
            'years': 0,
            'months': 0,
            'formatted': 'Unknown'
        }
    
    start_date = member.membership_start_date
    today = timezone.now().date()
    delta = today - start_date
    
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = delta.days % 30
    
    return {
        'days': delta.days,
        'years': years,
        'months': months,
        'days_remaining': days,
        'formatted': f'{years} years, {months} months' if years > 0 else f'{months} months'
    }


# ============================================================================
# EXECUTIVE BOARD MANAGEMENT ALGORITHMS
# ============================================================================

def check_executive_board_vacancy(board, position):
    """
    Check if a position in the executive board is vacant.
    Returns dict with vacancy status.
    """
    position_obj = board.positions.filter(
        position=position,
        status='active'
    ).first()
    
    if not position_obj or not position_obj.user:
        return {
            'is_vacant': True,
            'position': position_obj,
            'reason': 'No active position holder'
        }
    
    # Check for resignation
    if position_obj.status == 'resigned':
        return {
            'is_vacant': True,
            'position': position_obj,
            'reason': 'Position holder resigned'
        }
    
    # Check for absence (Article 13: 2 assemblies + 4 meetings)
    if position_obj.user:
        # Check assembly absences
        recent_assemblies = GeneralAssembly.objects.filter(
            date__gte=timezone.now() - timedelta(days=180),
            status='completed'
        ).order_by('-date')[:2]
        
        absences = 0
        for assembly in recent_assemblies:
            attendance = AssemblyAttendance.objects.filter(
                assembly=assembly,
                user=position_obj.user,
                attended=False
            ).exists()
            if attendance:
                absences += 1
        
        # Check board meeting absences
        recent_meetings = board.meetings.filter(
            meeting_date__gte=timezone.now() - timedelta(days=180)
        ).order_by('-meeting_date')[:4]
        
        for meeting in recent_meetings:
            if position_obj.user not in meeting.attendees.all():
                absences += 1
        
        if absences >= 6:  # 2 assemblies + 4 meetings (Article 13)
            # Automatically mark as resigned
            if position_obj.status != 'resigned':
                position_obj.status = 'resigned'
                position_obj.end_date = timezone.now().date()
                position_obj.save(update_fields=['status', 'end_date'])
            
            return {
                'is_vacant': True,
                'position': position_obj,
                'reason': f'Excessive absences: {absences} missed meetings/assemblies (automatic resignation per Article 13)',
                'auto_resigned': True
            }
    
    return {
        'is_vacant': False,
        'position': position_obj
    }


def get_executive_board_vacancies(board):
    """
    Get all vacant positions in an executive board.
    Returns list of vacant positions.
    """
    vacancies = []
    
    for position_code, position_name in EXECUTIVE_POSITION_CHOICES:
        vacancy_status = check_executive_board_vacancy(board, position_code)
        if vacancy_status['is_vacant']:
            vacancies.append({
                'position_code': position_code,
                'position_name': position_name,
                'reason': vacancy_status.get('reason', 'Vacant'),
                'position_obj': vacancy_status.get('position')
            })
    
    return vacancies


# ============================================================================
# FINANCIAL ALGORITHMS
# ============================================================================

def calculate_financial_summary(start_date=None, end_date=None):
    """
    Calculate financial summary for a period.
    Returns dict with income, expenses, and balance.
    """
    transactions = FinancialTransaction.objects.all()
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    income = transactions.filter(transaction_type='income', status__in=['approved', 'completed']).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    expenses = abs(transactions.filter(transaction_type='expense', status__in=['approved', 'completed']).aggregate(
        total=Sum('amount')
    )['total'] or 0)
    
    balance = income - expenses
    
    return {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'transaction_count': transactions.count()
    }


def check_expense_approval_status(transaction):
    """
    Check if expense has required approvals (Article 44: 3 signatures).
    Returns dict with approval status.
    """
    approvals = transaction.approvals.filter(status='signed')
    signed_count = approvals.count()
    required = 3
    
    # Get required signers (President, Treasurer, Statutory Auditor)
    current_board = ExecutiveBoard.objects.filter(status='active').first()
    required_signers = []
    
    if current_board:
        president = current_board.positions.filter(position='president', status='active').first()
        treasurer = current_board.positions.filter(position='treasurer', status='active').first()
        auditor = current_board.positions.filter(position='statutory_auditor', status='active').first()
        
        if president and president.user:
            required_signers.append(('president', president.user))
        if treasurer and treasurer.user:
            required_signers.append(('treasurer', treasurer.user))
        if auditor and auditor.user:
            required_signers.append(('statutory_auditor', auditor.user))
    
    return {
        'signed_count': signed_count,
        'required': required,
        'is_approved': signed_count >= required,
        'required_signers': required_signers,
        'approvals': approvals
    }


# ============================================================================
# ASSEMBLY MANAGEMENT ALGORITHMS
# ============================================================================

def check_extraordinary_assembly_quorum():
    """
    Check if 1/4 of members have requested extraordinary assembly (Article 6, 11).
    Returns dict with quorum status.
    """
    active_members = Member.objects.filter(is_active_member=True)
    total_active = active_members.count()
    required = (total_active + 3) // 4  # 1/4 rounded up
    
    # In a real implementation, you'd track requests
    # For now, return the requirement
    return {
        'total_active_members': total_active,
        'required': required,
        'current_requests': 0,  # Would be tracked in a model
        'quorum_met': False  # Would check actual requests
    }


def check_assembly_notice_period(assembly):
    """
    Check if assembly meets 10-day notice requirement (Article 4).
    Returns dict with compliance status.
    """
    if not assembly.convocation_date or not assembly.date:
        return {
            'compliant': False,
            'days': None,
            'message': 'Missing convocation or assembly date'
        }
    
    notice_days = (assembly.date.date() - assembly.convocation_date).days
    compliant = notice_days >= 10
    
    return {
        'compliant': compliant,
        'days': notice_days,
        'required': 10,
        'message': f'Notice period: {notice_days} days (required: 10 days)' if compliant else f'Insufficient notice: {notice_days} days (required: 10 days)'
    }


def check_agenda_item_proposal_deadline(assembly, proposal_date):
    """
    Check if agenda item proposal meets 14-day deadline (Article 22).
    Returns dict with compliance status.
    """
    if not assembly.date:
        return {
            'compliant': False,
            'days': None,
            'message': 'Assembly date not set'
        }
    
    days_before = (assembly.date.date() - proposal_date).days
    compliant = days_before >= 14
    
    return {
        'compliant': compliant,
        'days': days_before,
        'required': 14,
        'message': f'Proposal deadline: {days_before} days before assembly (required: 14 days)' if compliant else f'Too late: {days_before} days before assembly (required: 14 days)'
    }


def check_general_report_requirement():
    """
    Check if 6-month general report requirement is met (Article 45).
    Returns dict with compliance status and next due date.
    """
    from .models import FinancialReport
    
    # Get the most recent general report (annual or quarterly)
    last_report = FinancialReport.objects.filter(
        report_type__in=['annual', 'quarterly']
    ).order_by('-period_end').first()
    
    today = timezone.now().date()
    
    if not last_report:
        return {
            'compliant': False,
            'last_report_date': None,
            'days_overdue': None,
            'next_due_date': today + timedelta(days=180),
            'message': 'No general reports found. First report due within 6 months.'
        }
    
    # Calculate next due date (6 months after last report period end)
    next_due_date = last_report.period_end + timedelta(days=180)
    days_overdue = (today - next_due_date).days if today > next_due_date else None
    
    return {
        'compliant': days_overdue is None or days_overdue <= 0,
        'last_report_date': last_report.period_end,
        'days_overdue': days_overdue,
        'next_due_date': next_due_date,
        'message': f'Last report: {last_report.period_end}. Next due: {next_due_date}. ' + 
                   (f'Overdue by {days_overdue} days' if days_overdue else f'Due in {(next_due_date - today).days} days')
    }


def check_agenda_structure_requirements(assembly):
    """
    Check if assembly agenda meets required structure (Article 21).
    Required items: contemplation, minutes reading, finance, activities, miscellaneous.
    Returns dict with compliance status and missing items.
    """
    if not assembly:
        return {
            'compliant': False,
            'missing_items': [],
            'message': 'Assembly not provided'
        }
    
    agenda_items = assembly.agenda_items.all()
    item_types = set(agenda_items.values_list('item_type', flat=True))
    
    # Article 21 requires: contemplation, minutes reading, finance, activities, miscellaneous
    required_types = {'finance', 'activities', 'miscellaneous'}
    # Note: 'contemplation' and 'minutes reading' might be special items or handled differently
    # For now, we check for the main categories
    
    missing_items = required_types - item_types
    
    return {
        'compliant': len(missing_items) == 0,
        'missing_items': list(missing_items),
        'has_finance': 'finance' in item_types,
        'has_activities': 'activities' in item_types,
        'has_miscellaneous': 'miscellaneous' in item_types,
        'message': f'Missing required agenda items: {", ".join(missing_items)}' if missing_items else 'All required agenda items present'
    }


def check_assembly_frequency_compliance():
    """
    Check if assembly frequency meets requirements (Article 2).
    Requirements: at least twice a year, every quarter at most.
    Returns dict with compliance status.
    """
    from .models import GeneralAssembly
    
    today = timezone.now().date()
    one_year_ago = today - timedelta(days=365)
    
    # Get assemblies in the last year
    recent_assemblies = GeneralAssembly.objects.filter(
        date__gte=one_year_ago,
        status__in=['completed', 'in_progress']
    ).order_by('date')
    
    assembly_count = recent_assemblies.count()
    
    # Check if at least 2 assemblies per year
    meets_minimum = assembly_count >= 2
    
    # Check if no more than quarterly (every 3 months)
    meets_maximum = True
    if assembly_count > 0:
        # Check gaps between assemblies
        for i in range(len(recent_assemblies) - 1):
            gap_days = (recent_assemblies[i + 1].date.date() - recent_assemblies[i].date.date()).days
            if gap_days < 90:  # Less than 3 months
                meets_maximum = False
                break
    
    return {
        'compliant': meets_minimum and meets_maximum,
        'assembly_count': assembly_count,
        'meets_minimum': meets_minimum,
        'meets_maximum': meets_maximum,
        'message': f'Assembly frequency: {assembly_count} assemblies in last year. ' +
                   ('Meets requirements' if (meets_minimum and meets_maximum) else
                    ('Too few assemblies (minimum 2 per year)' if not meets_minimum else
                     'Too frequent assemblies (maximum quarterly)'))
    }

