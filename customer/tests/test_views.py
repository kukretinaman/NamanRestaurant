from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from customer.models import Restaurant, FoodItem, Order, Review, Feedback, UserProfile


class RestaurantListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City',
            cuisine='Italian',
            description='A test restaurant',
            avg_price=Decimal('25.50')
        )

    def test_restaurant_list_view(self):
        """Test restaurant list view renders correctly"""
        response = self.client.get(reverse('restaurant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')

    def test_restaurant_list_search(self):
        """Test restaurant search functionality"""
        response = self.client.get(reverse('restaurant_list'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')

    def test_restaurant_list_cuisine_filter(self):
        """Test restaurant cuisine filtering"""
        response = self.client.get(reverse('restaurant_list'), {'cuisine': 'Italian'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')


class MenuViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            description='A delicious pizza',
            price=Decimal('15.99'),
            is_veg=True
        )

    def test_menu_view_authenticated(self):
        """Test menu view for authenticated user"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('menu', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Pizza')

    def test_menu_view_unauthenticated(self):
        """Test menu view for unauthenticated user"""
        response = self.client.get(reverse('menu', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Pizza')


class OrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            price=Decimal('15.99'),
            is_veg=True
        )
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            total_price=Decimal('31.98'),
            status='Pending'
        )

    def test_orders_view_authenticated(self):
        """Test orders view for authenticated user"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)

    def test_orders_view_unauthenticated(self):
        """Test orders view for unauthenticated user"""
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 302)

    def test_cancel_order_authenticated(self):
        """Test cancel order for authenticated user"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.post(reverse('cancel_order', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Cancelled')


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_view_post_valid_credentials(self):
        """Test login view POST with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        """Test logout view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)