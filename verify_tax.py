import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ucz_cms.settings')
django.setup()

from hr.models import Employee, PayrollPeriod, Payslip
from hr.views import calculate_paye
from django.utils import timezone

def test_calculations():
    print("--- Starting Verification ---")
    
    # 1. Setup Data
    basic = 10000
    housing = 2000
    emp, _ = Employee.objects.get_or_create(
        email="tax_test@example.com",
        defaults={
            'first_name': "Tax", 'last_name': "Payer", 'role': "Manager",
            'date_joined': timezone.now().date(),
            'basic_salary': basic, 'housing_allowance': housing
        }
    )
    # Ensure allowances are set if it existed
    emp.basic_salary = basic
    emp.housing_allowance = housing
    emp.save()
    
    # 2. Simulate View Logic (Copy-Paste of logic for verification)
    gross = emp.basic_salary + emp.housing_allowance
    
    napsa_max_income = 27072
    napsa_income = min(gross, napsa_max_income)
    pension = Decimal(float(napsa_income) * 0.05).quantize(Decimal("0.01"))
    
    nhima = Decimal(float(emp.basic_salary) * 0.01).quantize(Decimal("0.01"))
    
    taxable_income = gross - pension
    paye = Decimal(calculate_paye(taxable_income)).quantize(Decimal("0.01"))
    
    net_pay = gross - (pension + nhima + paye)
    
    print(f"Gross: {gross}")
    print(f"Pension (5%): {pension} (Expected: 600.00)")
    print(f"NHIMA (1% Basic): {nhima} (Expected: 100.00)")
    print(f"Taxable: {taxable_income}")
    print(f"PAYE: {paye} (Expected: ~1844.00)")
    print(f"Net Pay: {net_pay} (Expected: ~9456.00)")
    
    if abs(paye - Decimal("1844.00")) < 1:
        print("SUCCESS: Tax calculation looks correct.")
    else:
        print("FAILURE: Tax calculation mismatch.")

if __name__ == "__main__":
    test_calculations()
