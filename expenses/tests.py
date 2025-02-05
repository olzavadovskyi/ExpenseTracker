from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from expenses.models import Category, Expense


class UserRegistrationTest(TestCase):
    def test_register_user(self):
        response = self.client.post(reverse('expenses:register'), {
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())


class UserLoginTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', password='password123')

    def test_login_user(self):
        response = self.client.post(reverse('expenses:sign_in'), {
            'username': 'testuser',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)


class CategoryCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_create_category(self):
        response = self.client.post(reverse('expenses:manage_categories'), {
            'category_name': 'Test Category',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Test Category', user=self.user).exists())


class ExpenseCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        self.category, created = Category.objects.get_or_create(
            name='Groceries',
            user=self.user
        )

    def test_create_expense(self):
        response = self.client.post(reverse('expenses:add_expense'), {
            'category': self.category.id,
            'name': 'Test Expense',
            'amount': '50.00',
            'currency': 'USD',
            'date': '2025-01-23',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expense.objects.filter(name='Test Expense', user=self.user).exists())


class CalendarViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_calendar_view(self):
        response = self.client.get(reverse('expenses:calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('days', response.context)
        self.assertIn('month_name', response.context)




