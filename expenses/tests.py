from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Transaction
from .forms import TransactionForm


class PersonalExpenseTrackerTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='alice', password='password123', email='alice@example.com')
        self.user2 = User.objects.create_user(username='bob', password='password123', email='bob@example.com')

        # Test clients
        self.client1 = Client()
        self.client1.login(username='alice', password='password123')

        self.client2 = Client()
        self.client2.login(username='bob', password='password123')

        # Seed sample transactions for User 1 (Alice)
        self.tx1 = Transaction.objects.create(
            user=self.user1,
            transaction_type='income',
            amount=Decimal('3500.00'),
            category='Salary',
            date=date(2026, 9, 1),
            description='Monthly Job Salary'
        )
        self.tx2 = Transaction.objects.create(
            user=self.user1,
            transaction_type='expense',
            amount=Decimal('150.00'),
            category='Food',
            date=date(2026, 9, 5),
            description='Supermarket Groceries'
        )
        self.tx3 = Transaction.objects.create(
            user=self.user1,
            transaction_type='expense',
            amount=Decimal('50.00'),
            category='Travel',
            date=date(2026, 9, 10),
            description='Subway Metro Pass'
        )

        # Seed transaction for User 2 (Bob)
        self.bob_tx = Transaction.objects.create(
            user=self.user2,
            transaction_type='income',
            amount=Decimal('2000.00'),
            category='Salary',
            date=date(2026, 9, 1),
            description='Bob Salary'
        )

    # 1. Model & Validation Tests
    def test_transaction_str(self):
        self.assertIn('Salary', str(self.tx1))
        self.assertIn('alice', str(self.tx1))

    def test_transaction_form_valid(self):
        form_data = {
            'transaction_type': 'expense',
            'amount': '45.00',
            'category': 'Entertainment',
            'date': '2026-09-15',
            'description': 'Movie Tickets'
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_transaction_form_rejects_negative_or_zero_amount(self):
        form_zero = TransactionForm(data={
            'transaction_type': 'expense',
            'amount': '0.00',
            'category': 'Bills',
            'date': '2026-09-15',
            'description': 'Zero check'
        })
        self.assertFalse(form_zero.is_valid())
        self.assertIn('amount', form_zero.errors)

        form_neg = TransactionForm(data={
            'transaction_type': 'expense',
            'amount': '-10.00',
            'category': 'Bills',
            'date': '2026-09-15',
            'description': 'Negative check'
        })
        self.assertFalse(form_neg.is_valid())
        self.assertIn('amount', form_neg.errors)

    # 2. Authentication & Registration Tests
    def test_registration_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password1': 'ComplexPassword!987',
            'password2': 'ComplexPassword!987',
        })
        # After registering, user is logged in and redirected to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='charlie').exists())

    def test_login_required_redirects_anonymous(self):
        anon_client = Client()
        response = anon_client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_logout_view(self):
        response = self.client1.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        # Verify subsequent dashboard request redirects to login
        dash_resp = self.client1.get(reverse('dashboard'))
        self.assertEqual(dash_resp.status_code, 302)

    # 3. User Data Isolation Tests (Critical Security Check)
    def test_user_cannot_see_other_users_transactions(self):
        response = self.client1.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        # Alice should see her transactions
        self.assertContains(response, 'Supermarket Groceries')
        # Alice should NEVER see Bob's transaction
        self.assertNotContains(response, 'Bob Salary')

    def test_user_cannot_edit_other_users_transaction(self):
        # Alice tries to edit Bob's transaction
        response = self.client1.get(reverse('transaction_edit', args=[self.bob_tx.pk]))
        self.assertEqual(response.status_code, 404)

        # Alice tries to POST an update to Bob's transaction
        post_response = self.client1.post(reverse('transaction_edit', args=[self.bob_tx.pk]), {
            'transaction_type': 'expense',
            'amount': '999.00',
            'category': 'Other',
            'date': '2026-09-01',
            'description': 'Hacked'
        })
        self.assertEqual(post_response.status_code, 404)
        # Bob's transaction remains unchanged
        self.bob_tx.refresh_from_db()
        self.assertEqual(self.bob_tx.amount, Decimal('2000.00'))

    def test_user_cannot_delete_other_users_transaction(self):
        # Alice tries to delete Bob's transaction
        response = self.client1.post(reverse('transaction_delete', args=[self.bob_tx.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Transaction.objects.filter(pk=self.bob_tx.pk).exists())

    # 4. Dashboard Calculations Tests
    def test_dashboard_calculations(self):
        response = self.client1.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_income'], Decimal('3500.00'))
        self.assertEqual(response.context['total_expenses'], Decimal('200.00'))
        self.assertEqual(response.context['current_balance'], Decimal('3300.00'))
        self.assertEqual(response.context['total_count'], 3)

    # 5. Transaction CRUD Tests
    def test_create_transaction(self):
        response = self.client1.post(reverse('transaction_add'), {
            'transaction_type': 'expense',
            'amount': '75.50',
            'category': 'Health',
            'date': '2026-09-18',
            'description': 'Pharmacy Medicine'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Transaction.objects.filter(user=self.user1, description='Pharmacy Medicine').exists())
        new_tx = Transaction.objects.get(description='Pharmacy Medicine')
        self.assertEqual(new_tx.amount, Decimal('75.50'))

    def test_update_transaction(self):
        response = self.client1.post(reverse('transaction_edit', args=[self.tx2.pk]), {
            'transaction_type': 'expense',
            'amount': '180.00',
            'category': 'Food',
            'date': '2026-09-05',
            'description': 'Supermarket Groceries & Snacks'
        })
        self.assertEqual(response.status_code, 302)
        self.tx2.refresh_from_db()
        self.assertEqual(self.tx2.amount, Decimal('180.00'))
        self.assertEqual(self.tx2.description, 'Supermarket Groceries & Snacks')

    def test_delete_transaction(self):
        response = self.client1.post(reverse('transaction_delete', args=[self.tx3.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Transaction.objects.filter(pk=self.tx3.pk).exists())

    # 6. Search and Filtering Tests
    def test_transaction_search(self):
        response = self.client1.get(reverse('transaction_list') + '?search=Subway')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Subway Metro Pass')
        self.assertNotContains(response, 'Supermarket Groceries')

    def test_transaction_filter_by_type(self):
        response = self.client1.get(reverse('transaction_list') + '?transaction_type=income')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monthly Job Salary')
        self.assertNotContains(response, 'Supermarket Groceries')

    def test_transaction_filter_by_category(self):
        response = self.client1.get(reverse('transaction_list') + '?category=Travel')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Subway Metro Pass')
        self.assertNotContains(response, 'Supermarket Groceries')

    # 7. Monthly Summary Tests
    def test_monthly_summary(self):
        response = self.client1.get(reverse('monthly_summary') + '?month=9&year=2026')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['income_sum'], Decimal('3500.00'))
        self.assertEqual(response.context['expense_sum'], Decimal('200.00'))
        self.assertEqual(response.context['balance'], Decimal('3300.00'))
        # Breakdown should have Food ($150) and Travel ($50)
        categories = [item['category'] for item in response.context['breakdown_list']]
        self.assertIn('Food', categories)
        self.assertIn('Travel', categories)
