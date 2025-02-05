# Django Expense Tracker

## Overview
The Django Expense Tracker is a web application that allows users to track their daily expenses, categorize them, view statistics, and manage finances efficiently. Users can register, log in, add expenses with currency conversion, and visualize financial data using a calendar and statistics.

## Features
- **User Authentication**: Register, login, and logout functionality.
- **Expense Management**: Add, edit, and delete expenses.
- **Category Management**: Create and manage expense categories.
- **Currency Conversion**: Fetch real-time exchange rates.
- **Calendar View**: View expenses for each day in an interactive calendar.
- **Statistics Dashboard**: Analyze spending habits over time.

## Technologies Used
- **Backend**: Django, Django ORM
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite (default), can be configured for PostgreSQL or MySQL
- **API Integration**: Exchange Rate API for currency conversion

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Django 4.0+
- Virtualenv (optional but recommended)

### Step 1: Clone the Repository
```sh
 git clone https://github.com/olzavadovskyi/expense-tracker.git
 cd Expense-Tracker
```

### Step 2: Create and Activate a Virtual Environment
```sh
 python -m venv env
 source env/bin/activate  # On macOS/Linux
 env\Scripts\activate    # On Windows
```

### Step 3: Install Dependencies
```sh
 pip install -r requirements.txt
```

### Step 4: Apply Migrations
```sh
 python manage.py migrate
```

### Step 5: Create a Superuser
```sh
 python manage.py createsuperuser
```
Follow the prompts to set up an admin account.

### Step 6: Run the Development Server
```sh
 python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`

## Usage
1. **Register/Login** to access the expense tracker.
2. **Add Expenses** with amount, category, and date.
3. **View Expenses** in a calendar format.
4. **Analyze Spending** through the statistics page.
5. **Manage Categories** to organize your expenses.
6. **Use Currency Conversion** to view expenses in different currencies.

## API Integration
### Currency Conversion
The application fetches exchange rates using:
```python
https://open.er-api.com/v6/latest/{from_currency}
```

## Contact
For any inquiries or issues, contact: **ol.zavadovskyi@gmail.com**

