# 💰 Personal Expense Tracker (Python + Django)

A clean, responsive, and beginner-friendly web application built with **Python**, **Django**, **SQLite**, and **Bootstrap 5** to help users track personal income, manage expenses, and analyze spending habits.

---

## 🚀 Key Features

1. **User Authentication & Privacy**
   - User registration, login, and logout powered by Django's secure authentication system.
   - **Strict Data Isolation**: Each user can only view, create, edit, and delete their own transactions. Users cannot see or tamper with other users' records.

2. **Dashboard Overview**
   - Lifetime summary cards: **Total Income**, **Total Expenses**, **Current Balance** (`Income - Expenses`), and **Total Transactions**.
   - Current calendar month quick-stats summary banner.
   - Recent transactions table displaying the 5 most recent activities.

3. **Transaction Management (Full CRUD)**
   - **Add Transaction**: Clean form with validation (Type: Income/Expense, Amount > 0, Category, Date, Description).
   - **View History**: Paginated transaction list (10 per page) with color-coded badges (Green for Income, Red for Expense).
   - **Edit Transaction**: Prepopulated form with strict ownership verification.
   - **Delete Transaction**: Dedicated delete confirmation screen displaying transaction details before removal.

4. **Search & Multi-Filter**
   - Instant search by transaction description or note.
   - Filter by type (**Income Only** / **Expense Only** / **All**).
   - Filter by predefined category (**Food**, **Travel**, **Shopping**, **Bills**, **Education**, **Health**, **Entertainment**, **Salary**, **Other**).
   - Filter by date range (**From Date** and **To Date**).
   - Dynamic filtered totals summary bar showing filtered income, expense, and net balance.

5. **Monthly Summary & Visual Analytics**
   - Month and Year selector to analyze any historical or current month.
   - Monthly KPI metric cards: Monthly Income, Monthly Expenses, and Monthly Balance.
   - Detailed category breakdown table with percentage share and progress bars.
   - Interactive **Chart.js Doughnut Chart** showing expense distribution across categories.

6. **Responsive UI**
   - Built with **Bootstrap 5.3** and **Bootstrap Icons**.
   - Seamlessly responsive on mobile screens, tablets, and desktop browsers.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13+, Django 6.1+
- **Database**: SQLite3 (zero external configuration required)
- **Frontend**: HTML5, CSS3, Bootstrap 5.3 (via CDN), Bootstrap Icons (via CDN)
- **Data Visualization**: Chart.js (via CDN)
- **Architecture**: Model-View-Template (MVT)

---

## 🗄️ Database & Model Explanation

The core model is `Transaction` located in `expenses/models.py`:

| Field | Type | Description |
|---|---|---|
| `user` | `ForeignKey(User, on_delete=models.CASCADE)` | Associates the transaction with the owning user. |
| `transaction_type` | `CharField` (choices: `income`, `expense`) | Identifies whether the transaction is an income or an expense. |
| `amount` | `DecimalField(max_digits=10, decimal_places=2)` | Stores the monetary amount (validated to be > 0.00). |
| `category` | `CharField` (predefined choices) | Categorizes the transaction (Food, Travel, Bills, etc.). |
| `date` | `DateField` | The date the transaction took place (defaults to today). |
| `description` | `CharField(max_length=255, blank=True)` | Optional note or memo for the transaction. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic timestamp of when the record was created. |

---

## 📂 Project Structure

```
personal_expense_tracker/
├── manage.py                          # Django command-line utility
├── requirements.txt                   # Project dependencies
├── README.md                          # Documentation and instructions
├── db.sqlite3                         # Local SQLite database
├── expense_tracker/                   # Project configuration
│   ├── __init__.py
│   ├── settings.py                    # Project settings & app config
│   ├── urls.py                        # Root URL dispatcher
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point
├── expenses/                          # Main Application
│   ├── __init__.py
│   ├── admin.py                       # Django Admin configuration
│   ├── apps.py                        # App configuration
│   ├── forms.py                       # ModelForms & Filter Forms
│   ├── models.py                      # Transaction data model
│   ├── urls.py                        # App route handlers
│   ├── views.py                       # Application views & business logic
│   ├── tests.py                       # Automated test suite (17 test cases)
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo_data.py      # Demo data seeder command
│   └── migrations/                    # Database migrations
├── templates/                         # HTML Templates
│   ├── base.html                      # Main layout with navbar & alerts
│   ├── registration/
│   │   ├── login.html                 # Login page
│   │   └── register.html              # Registration page
│   └── expenses/
│       ├── dashboard.html             # Overview dashboard
│       ├── transaction_list.html      # History, search & filters
│       ├── transaction_form.html      # Add & Edit form
│       ├── transaction_confirm_delete.html # Delete confirmation
│       └── monthly_summary.html       # Monthly report & Chart.js
└── static/
    └── css/
        └── style.css                  # Custom styling enhancements
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
Ensure you have Python (version 3.10 or higher) installed:
```bash
python --version
```

### 2. Navigate to Project Directory
```bash
cd "c:\Users\acer\OneDrive\Desktop\Projects\personal_expense_tracker"
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. (Optional) Populate Sample Demo Data
You can instantly populate a sample user with realistic income and expense transactions:
```bash
python manage.py seed_demo_data
```
> **Demo Account Credentials:**
> - **Username:** `demo_user`
> - **Password:** `password123`

### 6. Run the Development Server
```bash
python manage.py runserver
```
Open your web browser and visit: **http://127.0.0.1:8000/**

---

## 🧪 Running Automated Tests

A comprehensive test suite with 17 test cases is included to verify data isolation, calculations, CRUD operations, authentication, and filtering:

```bash
python manage.py test
```

Expected output:
```
Ran 17 tests in ...s
OK
```

---

## 💡 Optional Beginner-Friendly Improvements (Future Ideas)

1. **Export to CSV**: Add a button on the Transaction History page to download transactions as a `.csv` file.
2. **Monthly Budget Limits**: Allow users to set a monthly target spending limit and display an alert when expenses approach 80% or 100%.
3. **Receipt Image Upload**: Add an optional `image = models.ImageField(upload_to='receipts/', blank=True, null=True)` to attach photo receipts to transactions.
4. **Dark Mode Toggle**: Add a simple CSS/JavaScript theme toggle between light and dark modes.
