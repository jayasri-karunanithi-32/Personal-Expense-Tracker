from decimal import Decimal
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction


class UserRegistrationForm(UserCreationForm):
    """
    Form for registering a new user with username, email, and password.
    Includes Bootstrap styling.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to username and password fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class TransactionForm(forms.ModelForm):
    """
    Form for creating and editing a Transaction.
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'category', 'date', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Grocery shopping, Freelance payment'
            }),
        }
        labels = {
            'transaction_type': 'Type',
            'amount': 'Amount (₹)',
            'category': 'Category',
            'date': 'Date',
            'description': 'Description (Optional)',
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class TransactionFilterForm(forms.Form):
    """
    Form used on the Transaction History page to search and filter transactions.
    """
    TRANSACTION_TYPE_FILTER_CHOICES = [
        ('', 'All Types'),
        ('income', 'Income Only'),
        ('expense', 'Expense Only'),
    ]

    CATEGORY_FILTER_CHOICES = [('', 'All Categories')] + Transaction.CATEGORY_CHOICES

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search description or note...'
        })
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=TRANSACTION_TYPE_FILTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ChoiceField(
        required=False,
        choices=CATEGORY_FILTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
