from datetime import date, timedelta
from planner.models import Event, EventCategory

# Create Categories
cats = ['Sunday Service', 'Meeting', 'Bible Study', 'Community Outreach', 'Choir Practice']
categories = {}
for name in cats:
    cat, _ = EventCategory.objects.get_or_create(name=name, defaults={'color': 'blue'})
    categories[name] = cat

# Create Events
today = date.today()
events_data = [
    {
        'title': 'Sunday Service', 'description': 'Main Service',
        'category': categories['Sunday Service'], 'start_date': today + timedelta(days=2),
        'start_time': '09:00:00', 'location': 'Main Sanctuary'
    },
    {
        'title': 'Youth Bible Study', 'description': 'Weekly study',
        'category': categories['Bible Study'], 'start_date': today + timedelta(days=4),
        'start_time': '16:00:00', 'location': 'Youth Hall'
    },
    {
        'title': 'Choir Rehearsal', 'description': 'Preparation for next Sunday',
        'category': categories['Choir Practice'], 'start_date': today + timedelta(days=5),
        'start_time': '17:30:00', 'location': 'Main Sanctuary'
    },
    {
        'title': 'Deacons Meeting', 'description': 'Monthly planning',
        'category': categories['Meeting'], 'start_date': today + timedelta(days=7),
        'start_time': '14:00:00', 'location': 'Board Room'
    }
]

print("Populating events...")
for data in events_data:
    Event.objects.get_or_create(
        title=data['title'],
        start_date=data['start_date'],
        defaults=data
    )
    print(f"Added event: {data['title']} on {data['start_date']}")

print("Done.")
