import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ucz_cms.settings')
django.setup()

from hr.models import Employee, PayrollPeriod, Payslip
from django.contrib.auth.models import User

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

def generate_payroll_for_month(year, month):
    """Generate payroll for a specific month"""
    month_date = date(year, month, 1)
    
    # Get or create user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('admin', 'admin@example.com', 'admin')
    
    # Delete existing period if it exists
    PayrollPeriod.objects.filter(month=month_date).delete()
    
    # Create new period
    period = PayrollPeriod.objects.create(
        month=month_date,
        status='draft',
        processed_by=user
    )
    
    # Get all active employees
    employees = Employee.objects.filter(status='active')
    
    print(f"\n--- Generating Payroll for {month_date.strftime('%B %Y')} ---")
    print(f"Processing {employees.count()} employees...")
    
    for emp in employees:
        # Calculate gross pay
        gross = (emp.basic_salary + emp.housing_allowance + emp.transport_allowance + 
                emp.education_allowance + emp.medical_allowance + emp.other_allowance)
        
        # NAPSA: 5% of gross, capped at K1353.60 (max income K27,072)
        napsa_max = Decimal('1353.60')
        pension = min(gross * Decimal('0.05'), napsa_max)
        
        # NHIMA: 1% of basic salary
        nhima = emp.basic_salary * Decimal('0.01')
        
        # Taxable income = Gross - Pension
        taxable = gross - pension
        
        # PAYE
        paye = Decimal(str(calculate_paye(taxable)))
        
        # Net Pay
        net_pay = gross - pension - nhima - paye
        
        # Create payslip
        Payslip.objects.create(
            payroll_period=period,
            employee=emp,
            basic_salary=emp.basic_salary,
            housing_allowance=emp.housing_allowance,
            transport_allowance=emp.transport_allowance,
            education_allowance=emp.education_allowance,
            medical_allowance=emp.medical_allowance,
            other_allowance=emp.other_allowance,
            pension_deduction=pension,
            nhima_deduction=nhima,
            paye_tax=paye,
            gross_pay=gross,
            net_pay_calculated=net_pay,
            role_at_time=emp.role
        )
        
        print(f"  [OK] {emp.full_name}: Gross K{gross:,.2f} -> Net K{net_pay:,.2f}")
    
    print(f"\n[SUCCESS] Payroll generated successfully!")
    print(f"   Total Gross: K{sum(p.gross_pay for p in period.payslips.all()):,.2f}")
    print(f"   Total Net:   K{period.total_payout:,.2f}")
    
    return period

if __name__ == "__main__":
    print("=" * 60)
    print("PAYROLL GENERATION SCRIPT")
    print("=" * 60)
    
    # Generate for November 2024
    nov_period = generate_payroll_for_month(2024, 11)
    
    # Generate for October 2024
    oct_period = generate_payroll_for_month(2024, 10)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"October 2024:  {oct_period.payslips.count()} employees, K{oct_period.total_payout:,.2f}")
    print(f"November 2024: {nov_period.payslips.count()} employees, K{nov_period.total_payout:,.2f}")
    print("\nPayroll periods created successfully!")
    print("You can now view them in the Payroll Management dashboard.")
