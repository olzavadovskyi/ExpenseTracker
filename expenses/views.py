from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import requests
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
import calendar

from django.urls import reverse
from expenses.models import Expense, Category


def calendar_view(request):

    today = datetime.today()
    current_month = today.month
    current_year = today.year

    try:
        month = int(request.GET.get('month', current_month))
        year = int(request.GET.get('year', current_year))
    except ValueError:
        month = current_month
        year = current_year

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    min_year = current_year - 1
    max_year = current_year + 1
    if year < min_year:
        year = min_year
        month = 1
    elif year > max_year:
        year = max_year
        month = 12

    _, days_in_month = calendar.monthrange(year, month)

    days = [{"day": day, "formatted_day": f"{year}-{month:02d}-{day:02d}"} for day in range(1, days_in_month + 1)]

    month_name = datetime(year, month, 1).strftime('%B')

    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'days': days,
        'min_year': min_year,
        'max_year': max_year,
    }
    return render(request, 'expenses/calendar.html', context)


def fetch_exchange_rate(from_currency, to_currency="USD"):

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    api_url = f"https://open.er-api.com/v6/latest/{from_currency}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # exception for HTTP errors
        data = response.json()

        if data.get("result") == "error":
            print(f"Error: {data.get('error-type')}")
            return None

        rate = data.get("rates", {}).get(to_currency)
        if rate is None:
            print(f"Exchange rate not found for {from_currency} to {to_currency}")
            return None

        return rate
    except requests.RequestException as e:
        print(f"Error fetching exchange rate for {from_currency}: {e}")
        return None


def expense_detail(request):
    selected_date = request.GET.get('date', None)
    try:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else datetime.today().date()
    except ValueError:
        selected_date_obj = datetime.today().date()

    expenses = Expense.objects.filter(date=selected_date_obj, user=request.user)

    expenses_with_usd = []
    total_in_usd = Decimal('0.00')

    for expense in expenses:
        # Fetch exchange rate
        exchange_rate = fetch_exchange_rate(expense.currency)
        if exchange_rate:
            try:
                exchange_rate = Decimal(str(exchange_rate))
                amount_in_usd = Decimal(str(expense.amount)) * exchange_rate
            except Exception as e:
                print(f"Error in Decimal conversion: {e}")
                amount_in_usd = None
        else:
            amount_in_usd = None

        expenses_with_usd.append({
            "category": expense.category.name,
            "name": expense.name,
            "amount": expense.amount,
            "currency": expense.currency,
            "amount_in_usd": amount_in_usd if amount_in_usd else "N/A",
        })

        if isinstance(amount_in_usd, Decimal):
            total_in_usd += amount_in_usd

    context = {
        "selected_date": selected_date_obj,
        "expenses": expenses_with_usd,
        "total_in_usd": total_in_usd,
    }
    return render(request, "expenses/expense_detail.html", context)


def add_expense(request):
    selected_date = request.GET.get('date', None)
    try:
        # Selected  or default today's date
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else None
    except (ValueError, TypeError):
        selected_date_obj = None
        messages.error(request, "Invalid date format.")

    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        date = request.POST.get('date') or selected_date


        print("POST data:", request.POST)
        print("Selected date:", selected_date_obj)

        if not category_id or not name or not amount or not currency:
            messages.error(request, "All fields are required.")
            return redirect(request.path + f"?date={selected_date}")

        # Date is valid
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect(request.path + f"?date={selected_date}")

        try:
            category = Category.objects.get(id=category_id, user=request.user)
            Expense.objects.create(
                category=category,
                name=name,
                date=date,
                amount=amount,
                currency=currency,
                user=request.user
            )
            messages.success(request, "Expense added successfully!")
            return HttpResponseRedirect(f"{reverse('expenses:expense_detail')}?date={date}")
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    context = {
        'categories': categories,
        'selected_date': selected_date_obj,
    }
    return render(request, 'expenses/add_expense.html', context)


def manage_categories(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        if category_name:
            try:
                Category.objects.create(name=category_name, user=request.user)
                messages.success(request, f"Category '{category_name}' added successfully!")
            except IntegrityError:
                messages.error(request, f"Category '{category_name}' already exists.")
        return redirect('expenses:manage_categories')

    categories = Category.objects.filter(user=request.user)
    context = {
        'categories': categories,
    }
    return render(request, 'expenses/manage_categories.html', context)


def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        new_name = request.POST.get('category_name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, f"Category updated to '{new_name}'!")
            return redirect('expenses:manage_categories')

    context = {
        'category': category,
    }
    return render(request, 'expenses/edit_category.html', context)


def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == "POST":
        category_name = category.name
        category.delete()
        messages.success(request, f"Category '{category_name}' deleted successfully!")
        return redirect('expenses:manage_categories')

    context = {
        'category': category,
    }
    return render(request, 'expenses/delete_category.html', context)


def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('expenses:calendar')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'expenses/sign_in.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('expenses:register')

        try:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)  # Automatically log in the user
            print("Redirecting to calendar...")
            return redirect('expenses:calendar')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'expenses/register.html')


def statistics(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    category_id = request.GET.get('category', 'all')

    categories = Category.objects.filter(user=request.user)
    total_in_usd = Decimal('0.00')
    statistics_data = []

    filters = {'user': request.user}
    if start_date:
        filters['date__gte'] = start_date
    if end_date:
        filters['date__lte'] = end_date
    if category_id != 'all':
        filters['category__id'] = category_id

    expenses = Expense.objects.filter(**filters)
    expenses = expenses.order_by('date')

    for expense in expenses:
        exchange_rate = fetch_exchange_rate(expense.currency)
        if exchange_rate:
            try:
                exchange_rate = Decimal(str(exchange_rate))
                amount_in_usd = Decimal(str(expense.amount)) * exchange_rate
                total_in_usd += amount_in_usd
                statistics_data.append({
                    'name': expense.name,
                    'amount': expense.amount,
                    'currency': expense.currency,
                    'amount_in_usd': amount_in_usd,
                    'category': expense.category.name,
                    'date': expense.date,
                })
            except Exception as e:
                print(f"Error in Decimal conversion: {e}")

    context = {
        'categories': categories,
        'statistics_data': statistics_data,
        'total_in_usd': total_in_usd,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category_id,
    }

    return render(request, 'expenses/statistics.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('expenses:register')
