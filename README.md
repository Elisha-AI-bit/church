# UCZ Church Management System

A comprehensive church management system for United Church of Zambia (UCZ) Silverst Congregation built with Django, Django REST Framework, and Tailwind CSS.

## Features

### 📊 Dashboard
- Beautiful modern dashboard with real-time statistics
- Financial overview with income/expense tracking
- Membership statistics and recent activities
- Bank account balances and project status

### 👥 Membership Management
- Complete member profiles with personal information
- Dependent/family member tracking
- Position history tracking
- Member transfer management (from/to other churches)
- Search and filter capabilities

### 🏛️ Administration
- Office Bearer management (Chairperson, Secretary, Treasurer)
- Church Council tracking
- Lay Leaders management
- Church Elders and Sections
- Stewardship organization

### 👫 Groups & Committees
- **Groups**: MCF, YCF, WCF, Boys Brigade, Girls Brigade, Sunday School, Choir, Praise Team, Intercessors, Catechumen
- **Committees**: Stewardship, DWEC, CPDPC, Fundraising, Marriage & Guidance, CDSJ, Communications, Funerals, CTC, Lay Preachers, CRR, Catering
- Leadership structure for each (Convenor, Secretary, Treasurer)
- Membership tracking

### 💰 Finance Management
- Income tracking with 30+ predefined categories
- Expense tracking and categorization
- Automatic remittance calculations to higher courts (Synod, Presbytery, Consistory)
- Bank account management
- Assessment tracking
- Financial reports and summaries

### 🏗️ Projects
- Project management with budget tracking
- Internal and external funding sources
- Project assignments to groups/committees
- Progress monitoring and status updates

### 📈 Reports
- Membership reports
- Financial summaries
- Groups and committee reports
- Project status reports
- Customizable report templates

## Technology Stack

- **Backend**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Authentication**: Django built-in authentication system

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone or navigate to the project directory**
   ```bash
   cd c:\Users\ELISHA\Desktop\church
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash

   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

7. **Load initial data (optional)**
   ```bash
   python manage.py loaddata initial_data.json
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Web Interface: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Browser: http://127.0.0.1:8000/api/

## Initial Configuration

### 1. Add Sections
Navigate to Admin Panel → Membership → Sections and add your church sections.

### 2. Add Positions
Navigate to Admin Panel → Membership → Positions and add church positions.

### 3. Configure Income Categories
Navigate to Admin Panel → Finance → Income Categories and add:
- Envelopes, Tithe Offering, Loose Offering, Special Offering
- Holy Communion, Appeals, Good Friday, Easter, Harvest, Christmas
- Group offerings (MCF, YCF, WCF, etc.)
- Committee contributions

### 4. Configure Expense Categories
Navigate to Admin Panel → Finance → Expense Categories and add:
- Synod, Presbytery, Consistory
- Administration, Building, Groups, Committees
- Stewardship and other operational expenses

### 5. Configure Remittance Settings
Navigate to Admin Panel → Finance → Remittance Settings and configure:
- Synod percentage (e.g., 10%)
- Synod Holy Communion percentage
- Presbytery percentage
- Consistory percentage

Specify which income categories each remittance applies to.

### 6. Add Bank Accounts
Navigate to Admin Panel → Finance → Bank Accounts and add your church bank accounts.

### 7. Create Groups
Navigate to Admin Panel → Groups → Groups and create all church groups.

### 8. Create Committees
Navigate to Admin Panel → Committees → Committees and create all church committees.

## Usage Guide

### Recording Income
1. Go to Finance page
2. Click "Add Income"
3. Fill in the transaction details
4. Remittances will be calculated automatically based on your settings

### Recording Expenses
1. Go to Finance page
2. Click "Add Expense"
3. Fill in the expense details
4. Upload receipts if available

### Adding Members
1. Go to Membership page
2. Click "Add New Member"
3. Fill in member details
4. Add dependents/family members
5. Assign positions and groups

### Generating Reports
1. Go to Reports page
2. Select the report type
3. View the generated statistics
4. Export or print as needed

## API Endpoints

The system provides RESTful APIs for all modules:

- **Membership**: `/api/membership/`
- **Administration**: `/api/administration/`
- **Groups**: `/api/groups/`
- **Committees**: `/api/committees/`
- **Projects**: `/api/projects/`
- **Finance**: `/api/finance/`
- **Reports**: `/api/reports/`

Visit the API browser at http://127.0.0.1:8000/api/ to explore all available endpoints.

## Project Structure

```
church/
├── ucz_cms/                  # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
├── membership/               # Membership app
├── administration/           # Administration app
├── groups/                   # Groups app
├── committees/               # Committees app
├── projects/                 # Projects app
├── finance/                  # Finance app
├── reports/                  # Reports app
├── dashboard/                # Dashboard app
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── auth/                # Authentication templates
│   └── dashboard/           # Dashboard pages
├── static/                   # Static files (CSS, JS, images)
├── media/                    # Uploaded files
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies
```

## Security Considerations

⚠️ **Important for Production**:

1. Change the `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False` in production
3. Configure `ALLOWED_HOSTS` properly
4. Use PostgreSQL instead of SQLite
5. Set up proper backup procedures
6. Enable HTTPS
7. Configure email settings for notifications
8. Set up regular database backups

## Support & Documentation

For detailed information about each module, refer to Django's admin panel which includes comprehensive help text and field descriptions.

## License

This software is developed for United Church of Zambia (UCZ) Silverst Congregation.

## Credits

Developed using:
- Django Web Framework
- Django REST Framework
- Tailwind CSS
- Font Awesome Icons
- Google Fonts (Inter)

---

**Version**: 1.0.0 (MVP)  
**Last Updated**: December 2025
