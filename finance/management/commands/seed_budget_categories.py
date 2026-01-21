from django.core.management.base import BaseCommand
from finance.models import IncomeCategory, ExpenseCategory

class Command(BaseCommand):
    help = 'Seeds initial income and expense categories for budgeting'

    def handle(self, *args, **kwargs):
        income_streams = [
            "Envelopes", "Tithe Offering", "Loose Offering", "Special Offering", "Other Offering",
            "Holy Communion", "Appeals", "Good Friday", "Easter", "Harvest", "Christmas", "New Year",
            "Mid-week Prayers", "Men’s Christian Fellowship (MCF)", "Young Christian Fellowship (YCF)",
            "Women’s Christian Fellowship (WCF)", "Boys Brigade", "Girls Brigade", "Sunday School",
            "Church Choir", "Praise Team", "Intercessors", "Catechumen", "Stewardship",
            "Doctrine Worship and Evangelism", "Church Projects, Development and Planning (CPDPC)",
            "Fundraising", "Marriage and Guidance", "Community Development and Social Justice (CDSJ)",
            "Communications and Literature (CT)", "Funerals", "Church Training (CTC)", "Lay Preachers",
            "Church Rules and Regulations (CRR)", "Catering", "Combined Bible Study", "Sections", "Other"
        ]

        expenditure_streams_opex = [
            "Synod", "Synod Holy Communion", "Presbytery", "Consistory",
            "Synod Assessment", "Presbytery Assessment", "Consistory Assessment",
            "Rev Up Keep", "Reverend weekly activities", "Other Higher Courts Expenses",
            "Administration", "Stewardship", "Sunday School", "WCF", "MCF", "YCF",
            "BB", "GB", "CDSJ", "Choir", "Praise Team", "Committees", "Fund Raising",
            "Combined Bible Study", "Catechumen", "Sections", "Other"
        ]
        
        expenditure_streams_capex = [
            "Building", "Equipment", "Vehicles", "Major Renovations"
        ]

        self.stdout.write("Seeding Income Categories...")
        for name in income_streams:
            IncomeCategory.objects.get_or_create(name=name)

        self.stdout.write("Seeding Expense Categories (OPEX)...")
        for name in expenditure_streams_opex:
            ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'expense_type': 'opex'}
            )
            
        self.stdout.write("Seeding Expense Categories (CAPEX)...")
        for name in expenditure_streams_capex:
            ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'expense_type': 'capex'}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded budget categories'))
