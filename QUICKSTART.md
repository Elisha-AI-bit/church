# UCZ CMS - Quick Start Guide

## ✅ Installation Complete!

All dependencies have been installed and the database has been created with **26 models** across **7 modules**.

---

## Next Steps

### 1. Create a Superuser Account

Run this command to create an admin account:

```bash
python manage.py createsuperuser
```

Fill in:
- **Username**: (your choice)
- **Email**: (optional)
- **Password**: (your choice)

### 2. Start the Development Server

```bash
python manage.py runserver
```

### 3. Access the Application

- **Login Page**: http://127.0.0.1:8000/login/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Browser**: http://127.0.0.1:8000/api/

---

## Initial Configuration (via Admin Panel)

After logging in to the admin panel, configure the following in order:

### Step 1: Add Sections
`Admin → Membership → Sections → Add Section`

Add church sections (e.g., Section A, Section B, Youth Section)

### Step 2: Add Positions
`Admin → Membership → Positions → Add Position`

Add positions like:
- Reverend (Congregation level)
- Elder (Section level)
- Deacon (Section level)
- etc.

### Step 3: Configure Income Categories
`Admin → Finance → Income Categories → Add Income Category`

Add all 30+ income streams:
- Envelopes, Tithe Offering, Loose Offering
- Special Offerings, Holy Communion
- Group offerings (MCF, YCF, WCF, etc.)
- Event offerings (Easter, Christmas, Harvest)

### Step 4: Configure Expense Categories
`Admin → Finance → Expense Categories → Add Expense Category`

Add expense categories:
- Synod, Presbytery, Consistory (mark as remittance)
- Administration, Building, Utilities
- Group/Committee expenses

### Step 5: Configure Remittance Settings
`Admin → Finance → Remittance Settings → Add Remittance Setting`

Set up automatic remittances:
- **Synod** (e.g., 10% of selected categories)
- **Synod Holy Communion** (e.g., 100% of Holy Communion offerings)
- **Presbytery** (e.g., 5%)
- **Consistory** (e.g., 3%)

For each, select which income categories it applies to.

### Step 6: Add Bank Accounts
`Admin → Finance → Bank Accounts → Add Bank Account`

Add your church bank accounts with current balances.

### Step 7: Create Groups
`Admin → Groups → Groups → Add Group`

Create all 10 church groups (MCF, YCF, WCF, Brigades, Choir, etc.)

### Step 8: Create Committees
`Admin → Committees → Committees → Add Committee`

Create all 12 committees (Stewardship, DWEC, CPDPC, etc.)

---

## Testing the System

1. **Add a Member**: Admin → Membership → Members → Add Member
2. **Record Income**: Admin → Finance → Incomes → Add Income
   - Check that remittances are auto-created!
3. **Record Expense**: Admin → Finance → Expenses → Add Expense
4. **View Dashboard**: Navigate to the main dashboard to see statistics

---

## System Features

✅ **8 Modules**: Membership, Administration, Groups, Committees, Projects, Finance, Reports, Dashboard

✅ **60+ API Endpoints**: Full CRUD operations for all models

✅ **Modern UI**: Responsive design with Tailwind CSS

✅ **Automatic Remittances**: Financial calculations handled automatically

✅ **Position History**: Complete tracking of member positions over time

✅ **Budget Tracking**: Project monitoring with progress indicators

---

## Important Notes

- The system uses **SQLite** for development. For production, switch to **PostgreSQL**  
- All passwords should be changed before production deployment
- Regular database backups are recommended
- The automatic remittance feature creates expense records based on income

---

## Support

For detailed documentation, see:
- [README.md](file:///c:/Users/ELISHA/Desktop/church/README.md)
- [Walkthrough](file:///C:/Users/ELISHA/.gemini/antigravity/brain/8265393b-5066-4307-8079-81ee653bc998/walkthrough.md)

For admin help, check the Django admin panel tooltips and help text.

---

**System is ready for use! 🎉**
