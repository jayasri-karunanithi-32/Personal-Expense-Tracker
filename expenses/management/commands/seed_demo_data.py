from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from expenses.models import Transaction


class Command(BaseCommand):
    help = 'Seeds demo user and realistic transactions for testing and demonstration.'

    def handle(self, *args, **options):
        # 1. Create or get demo user
        username = 'demo_user'
        password = 'password123'
        email = 'demo@example.com'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user: '{username}' (password: '{password}')"))
        else:
            self.stdout.write(self.style.WARNING(f"Demo user '{username}' already exists."))

        # 2. Add sample transactions if none exist for this user
        if Transaction.objects.filter(user=user).exists():
            self.stdout.write(self.style.WARNING(f"Transactions already exist for '{username}'. Skipping seed data."))
            return

        today = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()

        sample_data = [
            # Incomes
            ('income', Decimal('4500.00'), 'Salary', today.replace(day=1), 'Monthly Salary Deposit'),
            ('income', Decimal('450.00'), 'Other', today - timedelta(days=4), 'Freelance Consulting Payment'),

            # Current Month Expenses
            ('expense', Decimal('120.50'), 'Food', today - timedelta(days=1), 'Weekly Supermarket Groceries'),
            ('expense', Decimal('35.00'), 'Food', today - timedelta(days=2), 'Dinner with friends'),
            ('expense', Decimal('65.00'), 'Travel', today - timedelta(days=5), 'Gas station fill-up'),
            ('expense', Decimal('80.00'), 'Bills', today - timedelta(days=8), 'Home Broadband Internet Bill'),
            ('expense', Decimal('45.00'), 'Entertainment', today - timedelta(days=10), 'Cinema IMAX Tickets & Popcorn'),
            ('expense', Decimal('150.00'), 'Shopping', today - timedelta(days=12), 'Casual Sneakers & Apparel'),
            ('expense', Decimal('70.00'), 'Health', today - timedelta(days=15), 'Pharmacy & Multivitamins'),
            ('expense', Decimal('199.99'), 'Education', today - timedelta(days=18), 'Online Web Development Bootcamp'),
            ('expense', Decimal('110.00'), 'Bills', today - timedelta(days=20), 'Electricity & Utility Bill'),
        ]

        created_count = 0
        for tx_type, amount, category, tx_date, desc in sample_data:
            Transaction.objects.create(
                user=user,
                transaction_type=tx_type,
                amount=amount,
                category=category,
                date=tx_date,
                description=desc
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} sample transactions for user '{username}'!"))
        self.stdout.write(self.style.SUCCESS(f"Log in with username: '{username}' and password: '{password}' to explore."))
