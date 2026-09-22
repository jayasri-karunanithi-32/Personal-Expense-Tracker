from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Transaction(models.Model):
    """
    Represents an Income or Expense transaction for an individual user.
    """

    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    CATEGORY_CHOICES = [
        ('Salary', 'Salary'),
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Bills', 'Bills'),
        ('Education', 'Education'),
        ('Health', 'Health'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text='The user who owns this transaction'
    )
    transaction_type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPE_CHOICES,
        default='expense',
        help_text='Whether this is an income or expense'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Amount must be greater than zero.')],
        help_text='Positive numeric amount (e.g. 25.50)'
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='Other',
        help_text='Transaction category'
    )
    date = models.DateField(
        default=timezone.now,
        help_text='Date when the transaction occurred'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional brief description or note'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Record creation timestamp'
    )

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()}: {self.category} (₹{self.amount}) on {self.date}"
