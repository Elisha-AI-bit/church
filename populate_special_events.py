from datetime import date, timedelta
from special_events.models import SpecialDay

# Create a future harvest event
SpecialDay.objects.get_or_create(
    name='Annual Harvest 2024',
    defaults={
        'date': date.today() + timedelta(days=30),
        'event_type': 'harvest',
        'description': 'Main Annual Harvest',
        'target_amount': 50000
    }
)

SpecialDay.objects.get_or_create(
    name='Christmas Service',
    defaults={
        'date': date(2025, 12, 25),
        'event_type': 'holiday',
        'description': 'Christmas Day Service',
        'target_amount': 10000
    }
)

print("Special Events populated.")
