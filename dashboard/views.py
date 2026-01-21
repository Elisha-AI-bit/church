from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from membership.models import Member, Dependent
from finance.models import Income, Expense, BankAccount, Remittance
from groups.models import Group, GroupMembership
from committees.models import Committee, CommitteeMembership
from projects.models import Project
from planner.models import Event
from special_events.models import SpecialDay
from datetime import datetime, timedelta


@login_required
def dashboard_home(request):
    """Main dashboard view"""
    # Get current month/year for filtering
    today = datetime.today()
    current_month_start = today.replace(day=1)
    
    # Membership stats
    total_members = Member.objects.count()
    new_members_this_month = Member.objects.filter(date_joined__gte=current_month_start).count()
    members_by_status = Member.objects.values('membership_status').annotate(count=Count('id'))
    
    # Finance stats
    total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    income_this_month = Income.objects.filter(transaction_date__gte=current_month_start).aggregate(total=Sum('amount'))['total'] or 0
    expense_this_month = Expense.objects.filter(transaction_date__gte=current_month_start).aggregate(total=Sum('amount'))['total'] or 0
    
    # Bank account balances
    bank_accounts = BankAccount.objects.filter(is_active=True)
    total_bank_balance = bank_accounts.aggregate(total=Sum('current_balance'))['total'] or 0
    
    # Remittances pending
    unpaid_remittances = Remittance.objects.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0
    
    # Projects stats
    active_projects = Project.objects.filter(status__in=['approved', 'in_progress']).count()
    total_project_budget = Project.objects.aggregate(total=Sum('total_budget'))['total'] or 0
    
    # Groups and Committees
    total_groups = Group.objects.count()
    total_committees = Committee.objects.count()
    
    # Recent activities
    # (Removed financial recent activity as per request)
    
    # 1. Sunday Services (Planner Events with 'Sunday' in category)
    upcoming_sundays = Event.objects.filter(
        start_date__gte=today.date(),
        category__name__icontains='Sunday',
        status__in=['planned', 'confirmed']
    ).order_by('start_date')[:5]

    # 2. General Planner (Planner Events WITHOUT 'Sunday' in category)
    upcoming_planner = Event.objects.filter(
        start_date__gte=today.date(),
        status__in=['planned', 'confirmed']
    ).exclude(category__name__icontains='Sunday').order_by('start_date')[:5]
    
    # 3. Special Events (From Special Events Module)
    upcoming_special = SpecialDay.objects.filter(
        date__gte=today.date(),
        is_active=True
    ).order_by('date')[:5]
    
    context = {
        'total_members': total_members,
        'new_members_this_month': new_members_this_month,
        'members_by_status': members_by_status,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': total_income - total_expense,
        'income_this_month': income_this_month,
        'expense_this_month': expense_this_month,
        'total_bank_balance': total_bank_balance,
        'unpaid_remittances': unpaid_remittances,
        'active_projects': active_projects,
        'total_project_budget': total_project_budget,
        'total_groups': total_groups,
        'total_committees': total_committees,
        'bank_accounts': bank_accounts,
        'upcoming_sundays': upcoming_sundays,
        'upcoming_planner': upcoming_planner,
        'upcoming_special': upcoming_special,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def membership_page(request):
    """Membership management page"""
    return render(request, 'dashboard/membership.html')


@login_required
def finance_page(request):
    """Finance management page"""
    return render(request, 'dashboard/finance.html')


@login_required
def groups_page(request):
    """Groups management page"""
    return render(request, 'dashboard/groups.html')


@login_required
def committees_page(request):
    """Committees management page"""
    return render(request, 'dashboard/committees.html')


@login_required
def projects_page(request):
    """Projects management page"""
    return render(request, 'dashboard/projects.html')


@login_required
def reports_page(request):
    """Reports page"""
    return render(request, 'dashboard/reports.html')


@login_required
def administration_page(request):
    """Administration page"""
    return render(request, 'dashboard/administration.html')


@login_required
def assets_page(request):
    """Assets management page"""
    return render(request, 'dashboard/assets.html')
