import random
from finance.models import AnnualBudget, BudgetIncomeItem, BudgetExpenseItem
from administration.models import Department
from core.models import Church

def seed_units_retro():
    church = Church.objects.first()
    if not church:
        print("No church found.")
        return

    depts = list(Department.objects.filter(church=church))
    if not depts:
        print("No departments found. Creating standard ones...")
        dept_names = ['Music & Praise', 'Youth Ministry', 'Women Fellowship', 'Men Fellowship', 'Sunday School', 'Building & Projects', 'Evangelism']
        for name in dept_names:
            dept, _ = Department.objects.get_or_create(church=church, name=name)
            depts.append(dept)

    for year in [2024, 2025]:
        try:
            budget = AnnualBudget.objects.get(church=church, year=year)
            print(f"Updating units for {year}...")
            
            # Income items
            income_items = BudgetIncomeItem.objects.filter(budget=budget)
            for item in income_items:
                if random.random() < 0.3:
                    item.department = random.choice(depts)
                    item.save()
            
            # Expense items
            expense_items = BudgetExpenseItem.objects.filter(budget=budget)
            for item in expense_items:
                if random.random() < 0.7:
                    item.department = random.choice(depts)
                    item.save()
                    
            print(f"Year {year} units updated.")
        except AnnualBudget.DoesNotExist:
            print(f"Budget for {year} not found.")

if __name__ == "__main__":
    seed_units_retro()
