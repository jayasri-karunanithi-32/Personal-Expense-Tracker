import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone

from .models import Transaction
from .forms import TransactionForm, TransactionFilterForm, UserRegistrationForm


def register_view(request):
    """
    Handle user registration.
    Redirects authenticated users to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Personal Expense Tracker, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Log out the user and redirect to login page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    User dashboard displaying overall financial overview,
    current balance, transaction count, recent transactions,
    and current month's quick summary.
    """
    user_transactions = Transaction.objects.filter(user=request.user)

    # Calculate overall lifetime totals
    income_agg = user_transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))
    expense_agg = user_transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))

    total_income = income_agg['total'] or Decimal('0.00')
    total_expenses = expense_agg['total'] or Decimal('0.00')
    current_balance = total_income - total_expenses
    total_count = user_transactions.count()

    # Recent 5 transactions
    recent_transactions = user_transactions[:5]

    # Current month quick summary
    today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()
    month_tx = user_transactions.filter(date__year=today.year, date__month=today.month)
    month_income = month_tx.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    month_expense = month_tx.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    month_balance = month_income - month_expense

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'total_count': total_count,
        'recent_transactions': recent_transactions,
        'current_month_name': today.strftime('%B %Y'),
        'month_income': month_income,
        'month_expense': month_expense,
        'month_balance': month_balance,
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def transaction_list_view(request):
    """
    Display full list of user's transactions with search, filter, and pagination.
    """
    queryset = Transaction.objects.filter(user=request.user)
    filter_form = TransactionFilterForm(request.GET or None)

    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search')
        tx_type = filter_form.cleaned_data.get('transaction_type')
        category = filter_form.cleaned_data.get('category')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')

        if search_query:
            queryset = queryset.filter(description__icontains=search_query)
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type)
        if category:
            queryset = queryset.filter(category=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

    # Aggregates for the filtered set
    filtered_income = queryset.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    filtered_expense = queryset.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    filtered_net = filtered_income - filtered_expense

    # Pagination: 10 transactions per page
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve filter GET parameters across pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_string = query_params.urlencode()

    context = {
        'filter_form': filter_form,
        'page_obj': page_obj,
        'filtered_income': filtered_income,
        'filtered_expense': filtered_expense,
        'filtered_net': filtered_net,
        'query_string': query_string,
    }
    return render(request, 'expenses/transaction_list.html', context)


@login_required
def transaction_create_view(request):
    """
    Create a new transaction for the current user.
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, f"{transaction.get_transaction_type_display()} of ₹{transaction.amount} added successfully.")
            return redirect('transaction_list')
        else:
            messages.error(request, "Failed to add transaction. Please check the errors below.")
    else:
        # Prepopulate default date to today
        today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()
        form = TransactionForm(initial={'date': today})

    context = {
        'form': form,
        'page_title': 'Add New Transaction',
        'button_text': 'Save Transaction',
    }
    return render(request, 'expenses/transaction_form.html', context)


@login_required
def transaction_update_view(request, pk):
    """
    Edit an existing transaction.
    Enforces user data isolation by matching pk and user.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, f"Transaction updated successfully.")
            return redirect('transaction_list')
        else:
            messages.error(request, "Failed to update transaction. Please check the errors below.")
    else:
        form = TransactionForm(instance=transaction)

    context = {
        'form': form,
        'transaction': transaction,
        'page_title': 'Edit Transaction',
        'button_text': 'Update Transaction',
    }
    return render(request, 'expenses/transaction_form.html', context)


@login_required
def transaction_delete_view(request, pk):
    """
    Delete a transaction after confirmation.
    Enforces user data isolation by matching pk and user.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        tx_type = transaction.get_transaction_type_display()
        amount = transaction.amount
        transaction.delete()
        messages.success(request, f"{tx_type} transaction of ₹{amount} was deleted.")
        return redirect('transaction_list')

    return render(request, 'expenses/transaction_confirm_delete.html', {'transaction': transaction})


@login_required
def monthly_summary_view(request):
    """
    Monthly Summary page:
    Allows user to select any month/year, displays monthly income, expenses,
    balance, and category-wise expense breakdown with a Chart.js doughnut chart.
    """
    today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()

    # Get selected year and month from query parameters, fallback to current
    try:
        selected_year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        selected_year = today.year

    try:
        selected_month = int(request.GET.get('month', today.month))
        if selected_month < 1 or selected_month > 12:
            selected_month = today.month
    except (ValueError, TypeError):
        selected_month = today.month

    # Filter transactions for user in selected month and year
    monthly_txs = Transaction.objects.filter(
        user=request.user,
        date__year=selected_year,
        date__month=selected_month
    )

    income_sum = monthly_txs.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expense_sum = monthly_txs.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = income_sum - expense_sum

    # Category breakdown for expenses
    category_breakdown = (
        monthly_txs.filter(transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Format data for Chart.js
    chart_labels = [item['category'] for item in category_breakdown]
    chart_data = [float(item['total']) for item in category_breakdown]

    # Calculate percentage for each category in breakdown
    breakdown_list = []
    for item in category_breakdown:
        cat_total = item['total']
        pct = (cat_total / expense_sum * 100) if expense_sum > 0 else Decimal('0.0')
        breakdown_list.append({
            'category': item['category'],
            'total': cat_total,
            'percentage': round(pct, 1),
        })

    # Available months for selector (1 to 12)
    month_choices = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    # Years choices: current year +/- 3 years
    year_choices = list(range(today.year - 3, today.year + 4))

    selected_month_name = dict(month_choices).get(selected_month, 'Unknown')

    context = {
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
        'month_choices': month_choices,
        'year_choices': year_choices,
        'income_sum': income_sum,
        'expense_sum': expense_sum,
        'balance': balance,
        'breakdown_list': breakdown_list,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data),
        'has_expenses': len(chart_data) > 0,
    }
    return render(request, 'expenses/monthly_summary.html', context)
