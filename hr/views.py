from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Employee, PayrollPeriod, Payslip
from .serializers import EmployeeSerializer, PayrollPeriodSerializer, PayslipSerializer
from finance.models import Expense, ExpenseCategory

from django.shortcuts import render

def employee_list_view(request):
    """Render employee list page"""
    return render(request, 'dashboard/hr/employee_list.html')

def payroll_dashboard_view(request):
    """Render payroll dashboard"""
    return render(request, 'dashboard/hr/payroll.html')

def payroll_report_view(request, period_id):
    """Render comprehensive payroll report for printing"""
    period = PayrollPeriod.objects.get(id=period_id)
    payslips = period.payslips.all().select_related('employee').order_by('employee__last_name')
    
    context = {
        'period': period,
        'payslips': payslips,
        'total_gross': sum(p.gross_pay for p in payslips),
        'total_napsa': sum(p.pension_deduction for p in payslips),
        'total_nhima': sum(p.nhima_deduction for p in payslips),
        'total_paye': sum(p.paye_tax for p in payslips),
        'total_net': sum(p.net_pay for p in payslips),
    }
    return render(request, 'dashboard/hr/payroll_report.html', context)

def payslip_view(request, payslip_id):
    """Render individual employee payslip"""
    payslip = Payslip.objects.select_related('employee', 'payroll_period').get(id=payslip_id)
    
    context = {
        'payslip': payslip,
        'employee': payslip.employee,
        'period': payslip.payroll_period,
    }
    return render(request, 'dashboard/hr/payslip.html', context)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'role']

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all().order_by('-month')
    serializer_class = PayrollPeriodSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['month', 'status']
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate draft payroll for a specific month"""
        month_str = request.data.get('month') # YYYY-MM-DD
        if not month_str:
            return Response({'error': 'Month is required'}, status=400)
            
        with transaction.atomic():
            # Create or Get Period
            period, created = PayrollPeriod.objects.get_or_create(month=month_str)
            
            if period.status != 'draft':
                return Response({'error': 'Cannot regenerate. Payroll is locked or paid.'}, status=400)
            
            # Delete existing draft slips to re-calculate
            period.payslips.all().delete()
            
            # Generate Slips for Active Employees
            active_employees = Employee.objects.filter(status='active')
            generated_count = 0
            
            for emp in active_employees:
                # 1. Allowances
                housing = emp.housing_allowance
                transport = emp.transport_allowance
                education = emp.education_allowance
                medical = emp.medical_allowance
                other = emp.other_allowance
                total_allowances = housing + transport + education + medical + other
                
                # 2. Gross
                gross = emp.basic_salary + total_allowances
                
                # 3. Statutory Deductions
                # NAPSA: 5% of Gross (Capped at ZMW 1353.60 as of 2024 <=> Max Income ZMW 27,072)
                napsa_max_income = Decimal('27072.00')
                napsa_income = min(gross, napsa_max_income)
                pension = napsa_income * Decimal('0.05')
                
                # NHIMA: 1% of Basic
                nhima = emp.basic_salary * Decimal('0.01')
                
                # 4. Tax (PAYE)
                # Taxable Income = Gross - Pension
                taxable_income = gross - pension
                paye = Decimal(str(calculate_paye(taxable_income)))
                
                # 5. Net Pay
                total_deductions = pension + nhima + paye
                net_pay = gross - total_deductions
                
                # 6. Leave Accrual (Projected)
                leave_balance = emp.leave_days_accrued
                leave_value = Decimal('0.00')
                if emp.pay_grade:
                     current_accrual = emp.pay_grade.monthly_leave_days
                     leave_balance += current_accrual
                     # Calculate Value: (Basic / 22) * Balance
                     daily_rate = emp.basic_salary / Decimal('22')
                     leave_value = daily_rate * leave_balance
                
                Payslip.objects.create(
                    payroll_period=period,
                    employee=emp,
                    basic_salary=emp.basic_salary,
                    role_at_time=emp.role,
                    
                    housing_allowance=housing,
                    transport_allowance=transport,
                    education_allowance=education,
                    medical_allowance=medical,
                    other_allowance=other,
                    
                    pension_deduction=pension,
                    nhima_deduction=nhima,
                    paye_tax=paye,
                    
                    gross_pay=gross,
                    net_pay_calculated=net_pay,
                    
                    leave_days_balance=leave_balance,
                    leave_pay_value=leave_value
                )
                generated_count += 1
            
            period.processed_by = request.user
            period.save()
            
            return Response({
                'message': f'Generated draft payroll for {generated_count} employees',
                'id': period.id
            })



    @action(detail=True, methods=['post'])
    def approve_and_pay(self, request, pk=None):
        """Lock payroll and Record Expense in Finance"""
        period = self.get_object()
        
        if period.status == 'paid':
            return Response({'error': 'Payroll already paid'}, status=400)
            
        with transaction.atomic():
            # 1. Update Status
            period.status = 'paid'
            period.paid_date = timezone.now().date()
            period.save()
            
            # 1.5 Commit Leave Accruals
            for slip in period.payslips.select_related('employee'):
                emp = slip.employee
                # Update employee balance to the value on the payslip (which included this month's accrual)
                emp.leave_days_accrued = slip.leave_days_balance
                emp.save()
            
            # 2. Integrate with Finance
            total_amount = period.total_payout
            if total_amount > 0:
                # Ensure Category Exists
                category, _ = ExpenseCategory.objects.get_or_create(
                    name="Salaries & Wages",
                    defaults={
                        'description': 'Automatic payroll expenses',
                        'expense_type': 'opex'
                    }
                )
                
                # Create Expense Record
                Expense.objects.create(
                    category=category,
                    amount=total_amount,
                    description=f"Payroll Payout - {period}",
                    transaction_date=period.paid_date,
                    created_by=request.user,
                    payment_method='Bank Transfer' # Default
                )
                
            return Response({'status': 'Payroll Approved and Paid. Finance record created.'})

    @action(detail=True, methods=['get'])
    def payslips(self, request, pk=None):
        """Get payslips for this period"""
        period = self.get_object()
        slips = period.payslips.all().select_related('employee')
        serializer = PayslipSerializer(slips, many=True)
        return Response(serializer.data)

class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer

def calculate_paye(income):
    """
    Calculate Zambian PAYE (Monthly) - 2024/2025 Bands
    0 - 5,100      : 0%
    5,101 - 7,100  : 20%
    7,101 - 9,200  : 30%
    Over 9,200     : 37%
    """
    tax = 0
    income = float(income)
    
    # Band 1: 0 - 5100
    if income <= 5100:
        return 0
    
    # Band 2: 5101 - 7100 (Max Tax: 2000 * 0.20 = 400)
    taxable_band_2 = min(income - 5100, 2000)
    tax += taxable_band_2 * 0.20
    
    if income <= 7100:
        return tax
        
    # Band 3: 7101 - 9200 (Max Tax: 2100 * 0.30 = 630)
    taxable_band_3 = min(income - 7100, 2100)
    tax += taxable_band_3 * 0.30
    
    if income <= 9200:
        return tax
        
    # Band 4: Over 9200
    taxable_band_4 = income - 9200
    tax += taxable_band_4 * 0.37
    
    return tax
