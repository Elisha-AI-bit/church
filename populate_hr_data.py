import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ucz_cms.settings')
django.setup()

from hr.models import Employee
from django.utils import timezone

def populate_employees():
    print("--- Clearing Old Data ---")
    Employee.objects.all().delete()
    print("--- Populating Test Employees ---")
    
    first_names = ["Mwape", "Chanda", "Mutale", "Mulenga", "Bwalya", "Mary", "John", "Peter", "Grace", "Joseph", "Esther", "David"]
    last_names = ["Phiri", "Banda", "Mulenga", "Sakala", "Tembo", "Lungu", "Ngoma", "Zulu", "Chama", "Mwila"]
    roles = ["Caretaker", "Administrator", "Musician", "Media Team", "Gardener", "Security", "Youth Pastor"]
    addresses = ["Avondale, Lusaka", "Chilenje South", "Kabwata Site & Service", "Woodlands Ext", "Chelstone Green", "Mtendere East", "Kamwala South"]
    
    for i in range(10):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        # Unique email
        email = f"{fname.lower()}.{lname.lower()}{random.randint(10,999)}@example.com"
        
        gender = random.choice(['Male', 'Female'])
        basic = random.choice([2000, 3500, 5000, 8000, 1500])
        
        emp = Employee.objects.create(
            first_name=fname,
            last_name=lname,
            gender=gender,
            email=email,
            phone=f"097{random.randint(1000000, 9999999)}",
            nrc_number=f"{random.randint(100000, 999999)}/10/1",
            address=random.choice(addresses),
            role=random.choice(roles),
            date_joined=timezone.now().date(),
            basic_salary=basic,
            housing_allowance=basic * 0.2 if basic > 3000 else 0,
            transport_allowance=500
        )
        print(f"Created: {emp} ({emp.role}) - {emp.gender}")

if __name__ == "__main__":
    populate_employees()
