from datetime import date
from membership.models import Member, Section

# Create sections if not exist
section_names = ['St. Peters', 'St. Pauls', 'St. Johns']
for name in section_names:
    Section.objects.get_or_create(name=name)

# Test Members Data
members_data = [
    {
        'first_name': 'John', 'last_name': 'Banda', 'gender': 'M', 
        'date_of_birth': date(1980, 5, 12), 'membership_status': 'communicant',
        'address': 'Plot 123, Kabwata', 'section_name': 'St. Peters'
    },
    {
        'first_name': 'Mary', 'last_name': 'Phiri', 'gender': 'F', 
        'date_of_birth': date(1985, 8, 22), 'membership_status': 'communicant',
        'address': 'Plot 456, Woodlands', 'section_name': 'St. Peters'
    },
    {
        'first_name': 'Peter', 'last_name': 'Mulenga', 'gender': 'M', 
        'date_of_birth': date(1990, 1, 15), 'membership_status': 'catechumen',
        'address': 'Plot 789, Chalala', 'section_name': 'St. Pauls'
    },
    {
        'first_name': 'Grace', 'last_name': 'Tembo', 'gender': 'F', 
        'date_of_birth': date(1995, 11, 30), 'membership_status': 'adherent',
        'address': 'Plot 101, Chilenje', 'section_name': 'St. Johns'
    },
    {
        'first_name': 'James', 'last_name': 'Zulu', 'gender': 'M', 
        'date_of_birth': date(1975, 3, 10), 'membership_status': 'communicant',
        'address': 'Plot 202, Libala', 'section_name': 'St. Pauls'
    }
]

print("Populating test members...")
for data in members_data:
    section = Section.objects.get(name=data.pop('section_name'))
    member, created = Member.objects.get_or_create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        defaults={
            'gender': data['gender'],
            'date_of_birth': data['date_of_birth'],
            'membership_status': data['membership_status'],
            'address': data['address'],
            'section': section,
            'date_joined': date.today()
        }
    )
    if created:
        print(f"Created: {member.full_name} -> {member.membership_number}")
    else:
        # If exists but has no number (e.g. from before), save to generate it
        if not member.membership_number:
            member.save()
            print(f"Updated: {member.full_name} -> {member.membership_number}")
        else:
            print(f"Exists: {member.full_name} -> {member.membership_number}")

# Backfill any others
print("\nBackfilling existing members...")
for m in Member.objects.filter(membership_number__isnull=True):
    m.save()
    print(f"Backfilled: {m.full_name} -> {m.membership_number}")
    
print("Done.")
