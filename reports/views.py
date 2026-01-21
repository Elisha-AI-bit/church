from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum
from membership.models import Member, Dependent
from finance.models import (
    Income, Expense, AnnualBudget, BudgetIncomeItem, BudgetExpenseItem
)
from administration.models import Department
from groups.models import GroupMembership
from committees.models import CommitteeMembership
from projects.models import Project
from .models import ReportTemplate, SavedReport
from .serializers import ReportTemplateSerializer, SavedReportSerializer


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['report_type', 'is_public']


class SavedReportViewSet(viewsets.ModelViewSet):
    queryset = SavedReport.objects.select_related('template', 'generated_by')
    serializer_class = SavedReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template', 'generated_by']


class ReportViewSet(viewsets.ViewSet):
    """Generate various reports"""
    
    @action(detail=False, methods=['get'])
    def membership_summary(self, request):
        """Membership statistics"""
        data = {
            'total_members': Member.objects.count(),
            'by_status': Member.objects.values('membership_status').annotate(count=Count('id')),
            'by_gender': Member.objects.values('gender').annotate(count=Count('id')),
            'by_section': Member.objects.values('section__name').annotate(count=Count('id')),
            'total_dependents': Dependent.objects.count(),
        }
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def financial_summary(self, request):
        """Financial statistics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        income_qs = Income.objects.all()
        expense_qs = Expense.objects.all()
        
        if start_date:
            income_qs = income_qs.filter(transaction_date__gte=start_date)
            expense_qs = expense_qs.filter(transaction_date__gte=start_date)
        
        if end_date:
            income_qs = income_qs.filter(transaction_date__lte=end_date)
            expense_qs = expense_qs.filter(transaction_date__lte=end_date)
        
        total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_expense = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
        
        data = {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': total_income - total_expense,
            'income_by_category': income_qs.values('category__name').annotate(total=Sum('amount')),
            'expense_by_category': expense_qs.values('category__name').annotate(total=Sum('amount')),
        }
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def groups_summary(self, request):
        """Groups statistics"""
        from groups.models import Group
        
        groups = Group.objects.all()
        data = []
        
        for group in groups:
            active_members = GroupMembership.objects.filter(group=group, is_active=True).count()
            data.append({
                'group_name': group.name,
                'description': group.description,
                'meeting_schedule': group.meeting_schedule,
                'active_members': active_members,
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def committees_summary(self, request):
        """Committees statistics"""
        from committees.models import Committee
        
        committees = Committee.objects.all()
        data = []
        
        for committee in committees:
            active_members = CommitteeMembership.objects.filter(committee=committee, is_active=True).count()
            data.append({
                'committee_name': committee.name,
                'description': committee.description,
                'meeting_schedule': committee.meeting_schedule,
                'active_members': active_members,
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def projects_summary(self, request):
        """Projects statistics"""
        data = {
            'total_projects': Project.objects.count(),
            'by_status': Project.objects.values('status').annotate(count=Count('id')),
            'total_budget': Project.objects.aggregate(total=Sum('total_budget'))['total'] or 0,
            'total_spent': Project.objects.aggregate(total=Sum('spent_amount'))['total'] or 0,
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def visitors_summary(self, request):
        """Weekly visitors statistics"""
        from planner.models import SundayReport
        
        # Get last 12 weeks of data
        reports = SundayReport.objects.order_by('-date')[:12]
        data = []
        for r in reports:
            data.append({
                'date': r.date,
                'visitors': r.attendance_visitors
            })
        
        # Reverse to show chronological order for charts
        data.reverse()
        
        return Response({
            'total_visitors': SundayReport.objects.aggregate(total=Sum('attendance_visitors'))['total'] or 0,
            'recent_trend': data
        })

    @action(detail=False, methods=['get'])
    def transfers_summary(self, request):
        """Member transfers statistics"""
        from membership.models import MemberTransfer
        
        incoming = MemberTransfer.objects.filter(transfer_type='incoming').count()
        outgoing = MemberTransfer.objects.filter(transfer_type='outgoing').count()
        
        recent_transfers = MemberTransfer.objects.select_related('member').order_by('-transfer_date')[:10]
        recent_data = []
        for t in recent_transfers:
            recent_data.append({
                'member_name': t.member.full_name,
                'type': t.get_transfer_type_display(),
                'from_church': t.from_church,
                'to_church': t.to_church,
                'date': t.transfer_date,
                'status': t.get_approval_status_display()
            })
            
        return Response({
            'total_incoming': incoming,
            'total_outgoing': outgoing,
            'recent_transfers': recent_data
        })
    @action(detail=False, methods=['get'])
    def budget_vs_actual(self, request):
        """Variance analysis of Budget vs Actuals"""
        year = request.query_params.get('year')
        if not year:
            import datetime
            year = datetime.date.today().year
            
        try:
            budget = AnnualBudget.objects.get(year=year)
        except AnnualBudget.DoesNotExist:
            return Response({'error': f'Budget for {year} not found'}, status=404)
            
        # Actuals
        income_actual = Income.objects.filter(transaction_date__year=year).aggregate(total=Sum('amount'))['total'] or 0
        expense_actual = Expense.objects.filter(transaction_date__year=year).aggregate(total=Sum('amount'))['total'] or 0
        
        # Budgeted
        income_budgeted = sum(item.total for item in budget.income_items.all())
        expense_budgeted = sum(item.total for item in budget.expense_items.all())
        
        return Response({
            'year': year,
            'income': {
                'budgeted': income_budgeted,
                'actual': income_actual,
                'variance': income_actual - income_budgeted
            },
            'expense': {
                'budgeted': expense_budgeted,
                'actual': expense_actual,
                'variance': expense_budgeted - expense_actual # Positive is savings
            }
        })

    @action(detail=False, methods=['get'])
    def departmental_performance(self, request):
        """Budget performance by department"""
        year = request.query_params.get('year', 2025)
        depts = Department.objects.all()
        data = []
        
        for dept in depts:
            budgeted = BudgetExpenseItem.objects.filter(budget__year=year, department=dept).aggregate(total=Sum('jan')+Sum('feb')+Sum('mar')+Sum('apr')+Sum('may')+Sum('jun')+Sum('jul')+Sum('aug')+Sum('sep')+Sum('oct')+Sum('nov')+Sum('dec'))['total'] or 0
            
            # Actuals (This assumes Expense model has a department field, which it might not yet)
            # For now return the budgeted allocation per department
            data.append({
                'department': dept.name,
                'budgeted': budgeted,
                'actual': 0, # Future enhancement
                'variance': -budgeted
            })
            
        return Response(data)
