from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from membership.models import Section, Position, Member, Dependent, PositionHistory, MemberTransfer
from administration.models import OfficeBearer, ChurchCouncil, LayLeader, ChurchElder, Stewardship
from groups.models import Group, GroupLeadership, GroupMembership
from committees.models import Committee, CommitteeLeadership, CommitteeMembership
from finance.models import (
    BankAccount, IncomeCategory, ExpenseCategory, RemittanceSettings,
    Income, Expense, Remittance, Assessment
)
from projects.models import Project, ProjectFunding, ProjectAssignment
from reports.models import ReportTemplate, SavedReport


class Command(BaseCommand):
    help = 'Load demo data into the Church Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('Loading demo data...'))
        
        # Create or get admin user
        self.admin_user = self.create_admin_user()
        
        # Load data in order (respecting dependencies)
        self.load_membership_data()
        self.load_administration_data()
        self.load_groups_data()
        self.load_committees_data()
        self.load_finance_data()
        self.load_projects_data()
        self.load_reports_data()
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Demo data loaded successfully!'))
        self.print_summary()

    def clear_data(self):
        """Clear all demo data"""
        models_to_clear = [
            SavedReport, ReportTemplate,
            ProjectAssignment, ProjectFunding, Project,
            Remittance, Assessment, Expense, Income,
            RemittanceSettings, ExpenseCategory, IncomeCategory, BankAccount,
            CommitteeMembership, CommitteeLeadership, Committee,
            GroupMembership, GroupLeadership, Group,
            Stewardship, ChurchElder, LayLeader, ChurchCouncil, OfficeBearer,
            MemberTransfer, PositionHistory, Dependent, Member, Position, Section,
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'  Deleted {count} {model.__name__} records')

    def create_admin_user(self):
        """Create or get admin user"""
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@church.org',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('  + Created admin user (username: admin, password: admin123)'))
        return user

    def load_membership_data(self):
        """Load membership module data"""
        self.stdout.write('\n[Membership] Loading Membership Data...')
        
        # Create Sections
        sections_data = [
            ('Men Fellowship', 'Men\'s ministry and fellowship'),
            ('Women Fellowship', 'Women\'s ministry and fellowship'),
            ('Youth Fellowship', 'Youth ministry ages 18-35'),
            ('Children Ministry', 'Children ministry ages 0-17'),
            ('Choir', 'Church choir and music ministry'),
        ]
        
        self.sections = {}
        for name, desc in sections_data:
            section = Section.objects.create(name=name, description=desc)
            self.sections[name] = section
        self.stdout.write(f'  + Created {len(sections_data)} sections')
        
        # Create Positions
        positions_data = [
            ('Pastor', 'congregation', 'Senior pastor of the church'),
            ('Elder', 'congregation', 'Church elder'),
            ('Deacon', 'congregation', 'Church deacon'),
            ('Secretary', 'congregation', 'Church secretary'),
            ('Treasurer', 'congregation', 'Church treasurer'),
            ('Section Leader', 'section', 'Leader of a church section'),
            ('Committee Chair', 'committee', 'Chairperson of committee'),
            ('Group Leader', 'group', 'Leader of a church group'),
            ('Choir Director', 'section', 'Director of church choir'),
            ('Youth Leader', 'section', 'Leader of youth fellowship'),
        ]
        
        self.positions = {}
        for title, level, desc in positions_data:
            position = Position.objects.create(title=title, level=level, description=desc)
            self.positions[title] = position
        self.stdout.write(f'  + Created {len(positions_data)} positions')
        
        # Create Members with Zambian names
        zambian_first_names_male = [
            'Mwamba', 'Kondwani', 'Chisomo', 'Thandiwe', 'Lusungu', 'Bwalya',
            'Mulenga', 'Chanda', 'Mwila', 'Kabwe', 'Mutale', 'Musonda',
            'Chilufya', 'Lubasi', 'Mukuka', 'Nsofwa', 'Chomba', 'Mwape'
        ]
        
        zambian_first_names_female = [
            'Natasha', 'Tamara', 'Chipo', 'Thandiwe', 'Chilufya', 'Mulenga',
            'Esther', 'Ruth', 'Naomi', 'Grace', 'Faith', 'Hope',
            'Joyce', 'Rose', 'Martha', 'Mary', 'Susan', 'Agnes'
        ]
        
        zambian_last_names = [
            'Phiri', 'Banda', 'Mwanza', 'Tembo', 'Mwale', 'Zulu',
            'Nyirenda', 'Sakala', 'Ng\'ombe', 'Ngoma', 'Kunda', 'Sichone',
            'Musonda', 'Mulenga', 'Bwalya', 'Chanda', 'Siame', 'Katongo',
            'Lungu', 'Chilufya', 'Mumba', 'Kabwe', 'Simpemba', 'Shamende'
        ]
        
        zambian_addresses = [
            'Plot 123, Meanwood, Lusaka',
            'House 45, Roma, Lusaka',
            'Plot 78, Chelston, Lusaka',
            'House 23, Olympia Park, Lusaka',
            'Plot 56, Woodlands, Lusaka',
            'House 89, Avondale, Lusaka',
            'Plot 34, Rhodes Park, Lusaka',
            'House 67, Kabulonga, Lusaka',
        ]
        
        self.members = []
        for i in range(40):
            gender = random.choice(['M', 'F'])
            first_name = random.choice(zambian_first_names_male if gender == 'M' else zambian_first_names_female)
            last_name = random.choice(zambian_last_names)
            
            # Age between 18 and 75
            age = random.randint(18, 75)
            date_of_birth = datetime.now().date() - timedelta(days=age*365)
            
            # Join date in past 5 years
            days_ago = random.randint(0, 5*365)
            date_joined = datetime.now().date() - timedelta(days=days_ago)
            
            member = Member.objects.create(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                phone=f'+260 {random.randint(95,97)}{random.randint(1000000,9999999)}',
                email=f'{first_name.lower()}.{last_name.lower()}@email.com',
                address=random.choice(zambian_addresses),
                place_of_work=random.choice(['Zambia Revenue Authority', 'Ministry of Health', 'Bank of Zambia', 
                                              'ZESCO', 'MTN Zambia', 'Airtel Zambia', 'Self Employed', 'N/A']),
                section=random.choice(list(self.sections.values())),
                membership_status=random.choice(['communicant', 'communicant', 'communicant', 'catechumen', 'adherent']),
                date_joined=date_joined,
                transfer_type=random.choice(['new', 'new', 'ucz_transfer', 'other_transfer']),
                transfer_from=random.choice(['', '', 'UCZ Matero', 'UCZ Kabwata', 'Baptist Church']) if random.random() > 0.7 else '',
                current_position=random.choice([None, None, None] + list(self.positions.values())[:5]),
                created_by=self.admin_user,
            )
            self.members.append(member)
        
        self.stdout.write(f'  + Created {len(self.members)} members')
        
        # Create Dependents
        dependents_count = 0
        for member in random.sample(self.members, 25):
            num_dependents = random.randint(1, 4)
            for j in range(num_dependents):
                child_age = random.randint(0, 17)
                child_dob = datetime.now().date() - timedelta(days=child_age*365)
                gender = random.choice(['M', 'F'])
                first_name = random.choice(zambian_first_names_male if gender == 'M' else zambian_first_names_female)
                
                Dependent.objects.create(
                    principal_member=member,
                    first_name=first_name,
                    last_name=member.last_name,
                    gender=gender,
                    date_of_birth=child_dob,
                    membership_status=random.choice(['child', 'child', 'catechumen']),
                )
                dependents_count += 1
        
        self.stdout.write(f'  + Created {dependents_count} dependents')
        
        # Create Position History
        history_count = 0
        for member in random.sample(self.members, 15):
            position = random.choice(list(self.positions.values())[:7])
            start_date = member.date_joined + timedelta(days=random.randint(30, 365))
            
            PositionHistory.objects.create(
                member=member,
                position=position,
                start_date=start_date,
                end_date=None if random.random() > 0.3 else start_date + timedelta(days=random.randint(365, 730)),
                notes=f'Appointed to {position.title}',
            )
            history_count += 1
        
        self.stdout.write(f'  + Created {history_count} position history records')
        
        # Create Member Transfers
        transfer_count = 0
        for member in random.sample(self.members, 5):
            MemberTransfer.objects.create(
                member=member,
                transfer_type=random.choice(['incoming', 'outgoing']),
                from_church='UCZ Kabwata' if random.random() > 0.5 else 'UCZ Matero',
                to_church='UCZ Chawama' if random.random() > 0.5 else 'UCZ Chelston',
                transfer_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
                approval_status=random.choice(['approved', 'approved', 'pending']),
                notes='Transfer approved by council',
            )
            transfer_count += 1
        
        self.stdout.write(f'  + Created {transfer_count} member transfers')

    def load_administration_data(self):
        """Load administration module data"""
        self.stdout.write('\n[Admin] Loading Administration Data...')
        
        # Office Bearers - use specific position choices from model
        office_bearer_positions = ['chairperson', 'secretary', 'vice_secretary', 'treasurer']
        for position in office_bearer_positions:
            member = random.choice(self.members)
            start_date = datetime.now().date() - timedelta(days=random.randint(365, 1095))
            
            OfficeBearer.objects.create(
                member=member,
                position=position,
                start_date=start_date,
                end_date=None if random.random() > 0.8 else start_date + timedelta(days=random.randint(365, 730)),
                is_active=random.random() > 0.2,
            )
        self.stdout.write('  + Created 4 office bearers')
        
        # Church Council
        for i in range(5):
            member = random.choice(self.members)
            ChurchCouncil.objects.create(
                member=member,
                role=random.choice(['Chairperson', 'Vice Chairperson', 'Secretary', 'Member', 'Member']),
                start_date=datetime.now().date() - timedelta(days=random.randint(180, 730)),
                is_active=True,
            )
        self.stdout.write('  + Created 5 church council members')
        
        # Lay Leaders
        for i in range(5):
            member = random.choice(self.members)
            LayLeader.objects.create(
                member=member,
                specialty=random.choice(['Preaching', 'Teaching', 'Counseling', 'Administration', 'Outreach']),
                start_date=datetime.now().date() - timedelta(days=random.randint(365, 1095)),
                is_active=True,
            )
        self.stdout.write('  + Created 5 lay leaders')
        
        # Church Elders
        for i in range(6):
            member = random.choice(self.members)
            ChurchElder.objects.create(
                member=member,
                section=random.choice(list(self.sections.values())),
                ordained_date=datetime.now().date() - timedelta(days=random.randint(730, 3650)),
                is_active=True,
            )
        self.stdout.write('  + Created 6 church elders')
        
        # Stewardship
        for i in range(7):
            member = random.choice(self.members)
            Stewardship.objects.create(
                member=member,
                role=random.choice(['convenor', 'member', 'member', 'member']),
                section=random.choice(list(self.sections.values())),
                start_date=datetime.now().date() - timedelta(days=random.randint(180, 730)),
                is_active=True,
            )
        self.stdout.write('  + Created 7 stewardship members')

    def load_groups_data(self):
        """Load groups module data"""
        self.stdout.write('\n[Groups] Loading Groups Data...')
        
        groups_data = [
            ('Prayer Warriors', 'prayer', 'Every Tuesday 18:00', 'Intercessory prayer group'),
            ('Bible Study Fellowship', 'bible_study', 'Every Wednesday 19:00', 'Weekly Bible study and discussion'),
            ('Youth Praise Team', 'youth', 'Every Saturday 14:00', 'Youth worship and praise'),
            ('Men\'s Ministry', 'fellowship', 'First Saturday 09:00', 'Men\'s fellowship and mentorship'),
            ('Women of Faith', 'fellowship', 'Second Saturday 10:00', 'Women\'s fellowship and support'),
            ('Senior Saints', 'fellowship', 'Every Thursday 15:00', 'Fellowship for senior citizens'),
        ]
        
        self.groups = []
        for name, group_type, schedule, desc in groups_data:
            group = Group.objects.create(
                name=name,
                description=desc,
                group_type=group_type,
                meeting_schedule=schedule,
            )
            self.groups.append(group)
            
            # Add leaders
            for i in range(random.randint(1, 2)):
                GroupLeadership.objects.create(
                    group=group,
                    member=random.choice(self.members),
                    role=random.choice(['Leader', 'Assistant Leader', 'Coordinator']),
                    start_date=datetime.now().date() - timedelta(days=random.randint(90, 730)),
                    is_active=True,
                )
            
            # Add members
            for i in range(random.randint(5, 12)):
                GroupMembership.objects.create(
                    group=group,
                    member=random.choice(self.members),
                    joined_date=datetime.now().date() - timedelta(days=random.randint(30, 730)),
                    is_active=random.random() > 0.1,
                )
        
        self.stdout.write(f'  + Created {len(self.groups)} groups with leaders and members')

    def load_committees_data(self):
        """Load committees module data"""
        self.stdout.write('\n[Committees] Loading Committees Data...')
        
        committees_data = [
            ('Finance Committee', 'finance', 'Monthly - Last Sunday', 'Oversees church finances'),
            ('Building Committee', 'building', 'Bi-weekly - Saturdays', 'Manages building projects'),
            ('Welfare Committee', 'welfare', 'Monthly - Second Sunday', 'Handles welfare matters'),
            ('Outreach Committee', 'missions', 'Monthly - First Sunday', 'Coordinates outreach activities'),
            ('Youth Committee', 'youth', 'Weekly - Fridays', 'Organizes youth activities'),
        ]
        
        self.committees = []
        for name, committee_type, schedule, desc in committees_data:
            committee = Committee.objects.create(
                name=name,
                description=desc,
                committee_type=committee_type,
                meeting_schedule=schedule,
            )
            self.committees.append(committee)
            
            # Add leadership
            for i in range(random.randint(2, 3)):
                CommitteeLeadership.objects.create(
                    committee=committee,
                    member=random.choice(self.members),
                    role=random.choice(['Chairperson', 'Vice Chairperson', 'Secretary', 'Treasurer']),
                    start_date=datetime.now().date() - timedelta(days=random.randint(180, 730)),
                    is_active=True,
                )
            
            # Add members
            for i in range(random.randint(4, 8)):
                CommitteeMembership.objects.create(
                    committee=committee,
                    member=random.choice(self.members),
                    joined_date=datetime.now().date() - timedelta(days=random.randint(60, 730)),
                    is_active=random.random() > 0.15,
                )
        
        self.stdout.write(f'  + Created {len(self.committees)} committees with leadership and members')

    def load_finance_data(self):
        """Load finance module data"""
        self.stdout.write('\n[Finance] Loading Finance Data...')
        
        # Bank Accounts
        self.bank_accounts = [
            BankAccount.objects.create(
                account_name='Main Operating Account',
                bank_name='Zanaco',
                branch='Cairo Road Branch',
                account_number='0123456789',
                account_type='savings',
                current_balance=45000.00,
                is_active=True,
            ),
            BankAccount.objects.create(
                account_name='Building Fund Account',
                bank_name='Stanbic Bank',
                branch='Longacres Branch',
                account_number='9876543210',
                account_type='savings',
                current_balance=125000.00,
                is_active=True,
            ),
            BankAccount.objects.create(
                account_name='Welfare Account',
                bank_name='First National Bank',
                branch='Woodlands Branch',
                account_number='5555666677',
                account_type='current',
                current_balance=15000.00,
                is_active=True,
            ),
        ]
        self.stdout.write(f'  + Created {len(self.bank_accounts)} bank accounts')
        
        # Income Categories
        income_categories_data = [
            ('Tithes', False),
            ('Offerings', False),
            ('Donations', False),
            ('Fundraising', False),
            ('Mission Offerings', True),
            ('Building Fund', False),
            ('Welfare Contributions', False),
        ]
        
        self.income_categories = []
        for name, is_remittance in income_categories_data:
            cat = IncomeCategory.objects.create(name=name, is_active=True)
            self.income_categories.append(cat)
        self.stdout.write(f'  + Created {len(self.income_categories)} income categories')
        
        # Expense Categories
        expense_categories_data = [
            ('Utilities', False),
            ('Salaries', False),
            ('Maintenance', False),
            ('Office Supplies', False),
            ('Remittances to Presbytery', True),
            ('Outreach Programs', False),
            ('Welfare Support', False),
        ]
        
        self.expense_categories = []
        for name, is_remittance in expense_categories_data:
            cat = ExpenseCategory.objects.create(name=name, is_remittance=is_remittance, is_active=True)
            self.expense_categories.append(cat)
        self.stdout.write(f'  + Created {len(self.expense_categories)} expense categories')
        
        # Remittance Settings
        RemittanceSettings.objects.create(
            remittance_type='Presbytery',
            percentage=10.0,
            is_active=True,
        )
        RemittanceSettings.objects.create(
            remittance_type='Synod',
            percentage=5.0,
            is_active=True,
        )
        self.stdout.write('  + Created 2 remittance settings')
        
        # Income Records
        income_count = 0
        for i in range(30):
            days_ago = random.randint(0, 365)
            transaction_date = datetime.now().date() - timedelta(days=days_ago)
            
            Income.objects.create(
                category=random.choice(self.income_categories),
                amount=random.choice([500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]),
                transaction_date=transaction_date,
                bank_account=random.choice(self.bank_accounts),
                payer_name=f'{random.choice(self.members).full_name}' if random.random() > 0.3 else 'Anonymous',
                payment_method=random.choice(['cash', 'mobile_money', 'bank_transfer', 'cheque']),
                receipt_number=f'RCP{1000+i}',
                description=random.choice(['Sunday Collection', 'Monthly Tithe', 'Special Offering', 'Donation']),
                remittances_calculated=random.random() > 0.3,
            )
            income_count += 1
        self.stdout.write(f'  + Created {income_count} income records')
        
        # Expense Records
        expense_count = 0
        for i in range(25):
            days_ago = random.randint(0, 365)
            transaction_date = datetime.now().date() - timedelta(days=days_ago)
            
            Expense.objects.create(
                category=random.choice(self.expense_categories),
                amount=random.choice([300, 500, 800, 1200, 1500, 2000, 3000, 5000]),
                transaction_date=transaction_date,
                bank_account=random.choice(self.bank_accounts),
                payee_name=random.choice(['ZESCO', 'Water Trust', 'Office Supplies Ltd', 'John Banda', 'ABC Hardware']),
                payment_method=random.choice(['cash', 'mobile_money', 'bank_transfer', 'cheque']),
                voucher_number=f'VCH{2000+i}',
                description=random.choice(['Electricity Bill', 'Water Bill', 'Office Supplies', 'Maintenance', 'Salary Payment']),
            )
            expense_count += 1
        self.stdout.write(f'  + Created {expense_count} expense records')
        
        # Assessments
        for i in range(8):
            Assessment.objects.create(
                assessment_type=random.choice(['Presbytery', 'Synod', 'Special Levy']),
                amount=random.choice([5000, 10000, 15000, 20000]),
                frequency=random.choice(['monthly', 'quarterly', 'annually']),
                due_date=datetime.now().date() + timedelta(days=random.randint(30, 180)),
                paid=random.random() > 0.4,
                paid_date=datetime.now().date() - timedelta(days=random.randint(0, 30)) if random.random() > 0.5 else None,
            )
        self.stdout.write('  + Created 8 assessment records')

    def load_projects_data(self):
        """Load projects module data"""
        self.stdout.write('\n[Projects] Loading Projects Data...')
        
        projects_data = [
            ('New Church Building', 'building', 'Planning and construction of new sanctuary', 500000, 'self_funded'),
            ('Community Water Project', 'community', 'Drilling borehole for community', 75000, 'donor_funded'),
            ('Youth Empowerment Program', 'youth', 'Skills training for youth', 50000, 'mixed_funded'),
            ('Welfare Support Initiative', 'welfare', 'Supporting vulnerable families', 30000, 'self_funded'),
        ]
        
        self.projects = []
        for name, proj_type, desc, budget, funding in projects_data:
            project = Project.objects.create(
                name=name,
                description=desc,
                project_type=proj_type,
                status=random.choice(['planning', 'ongoing', 'completed']),
                funding_type=funding,
                total_budget=budget,
                spent_amount=random.randint(int(budget*0.2), int(budget*0.8)),
                start_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
                end_date=datetime.now().date() + timedelta(days=random.randint(90, 730)),
            )
            self.projects.append(project)
            
            # Add funding records
            for i in range(random.randint(1, 3)):
                ProjectFunding.objects.create(
                    project=project,
                    source_type=random.choice(['church', 'donor', 'individual', 'grant']),
                    source_name=random.choice(['Church Budget', 'Mission Board', 'Anonymous Donor', 'Member Contribution']),
                    amount=random.randint(5000, 50000),
                    received_date=datetime.now().date() - timedelta(days=random.randint(0, 180)),
                )
            
            # Add assignments
            if random.random() > 0.5:
                ProjectAssignment.objects.create(
                    project=project,
                    responsible_entity_type='committee',
                    committee=random.choice(self.committees) if self.committees else None,
                    assigned_date=project.start_date,
                )
        
        self.stdout.write(f'  + Created {len(self.projects)} projects with funding and assignments')

    def load_reports_data(self):
        """Load reports module data"""
        self.stdout.write('\n[Reports] Loading Reports Data...')
        
        templates_data = [
            ('Monthly Financial Summary', 'financial', True, 'Summary of monthly income and expenses'),
            ('Membership Report', 'membership', True, 'Current membership statistics'),
            ('Project Status Report', 'projects', False, 'Status of all ongoing projects'),
            ('Attendance Report', 'attendance', True, 'Weekly attendance statistics'),
        ]
        
        for name, report_type, is_public, desc in templates_data:
            template = ReportTemplate.objects.create(
                name=name,
                description=desc,
                report_type=report_type,
                is_public=is_public,
                created_by=self.admin_user,
            )
            
            # Create a saved report
            if random.random() > 0.5:
                SavedReport.objects.create(
                    template=template,
                    title=f'{name} - {datetime.now().strftime("%B %Y")}',
                    content={'summary': 'Report data will be generated here'},
                    generated_by=self.admin_user,
                )
        
        self.stdout.write('  + Created 4 report templates and saved reports')

    def print_summary(self):
        """Print summary of loaded data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DEMO DATA SUMMARY'))
        self.stdout.write('='*50)
        
        summary = [
            ('Sections', Section.objects.count()),
            ('Positions', Position.objects.count()),
            ('Members', Member.objects.count()),
            ('Dependents', Dependent.objects.count()),
            ('Office Bearers', OfficeBearer.objects.count()),
            ('Church Council', ChurchCouncil.objects.count()),
            ('Groups', Group.objects.count()),
            ('Committees', Committee.objects.count()),
            ('Bank Accounts', BankAccount.objects.count()),
            ('Income Records', Income.objects.count()),
            ('Expense Records', Expense.objects.count()),
            ('Projects', Project.objects.count()),
            ('Report Templates', ReportTemplate.objects.count()),
        ]
        
        for label, count in summary:
            self.stdout.write(f'  {label:.<30} {count:>3}')
        
        self.stdout.write('='*50)
        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] You can now login to the admin panel:'))
        self.stdout.write('  URL: http://127.0.0.1:8000/admin/')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
