from django.test import TestCase, Client # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.urls import reverse # type: ignore
from decimal import Decimal
from customer.models import Restaurant, FoodItem, Order, OrderItem, Review, Feedback


class OwnerDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City',
            cuisine='Italian',
            avg_price=Decimal('25.50')
        )
        self.food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            description='A delicious pizza',
            price=Decimal('15.99'),
            is_veg=True
        )

    def test_owner_dashboard_requires_login(self):
        """Test owner dashboard requires login"""
        response = self.client.get(reverse('owner_dashboard', args=[self.restaurant.id]))
        self.assertIn(response.status_code, [302, 301])

    def test_owner_dashboard_logged_in(self):
        """Test owner dashboard when logged in"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('owner_dashboard', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')

    def test_owner_dashboard_unauthorized_user(self):
        """Test owner dashboard with unauthorized user"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('owner_dashboard', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_dashboard_with_orders(self):
        """Test owner dashboard with orders"""
        self.client.login(username='owner', password='testpass123')
        
        # Create an order
        order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            total_price=Decimal('31.98'),
            status='Completed'
        )
        OrderItem.objects.create(
            order=order,
            food_item=self.food_item,
            quantity=2
        )
        
        response = self.client.get(reverse('owner_dashboard', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')

    def test_owner_dashboard_analytics(self):
        """Test owner dashboard analytics"""
        self.client.login(username='owner', password='testpass123')
        
        # Create completed orders for analytics
        for i in range(3):
            order = Order.objects.create(
                customer=self.customer,
                restaurant=self.restaurant,
                total_price=Decimal('25.00'),
                status='Completed'
            )
            OrderItem.objects.create(
                order=order,
                food_item=self.food_item,
                quantity=1
            )
        
        response = self.client.get(reverse('owner_dashboard', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        # Check if analytics data is present
        self.assertIn('total_sales', response.context)


class MenuManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )

    def test_add_food_item_authenticated(self):
        """Test add food item for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('add_food_item', args=[self.restaurant.id]), {
            'name': 'New Pizza',
            'description': 'A new pizza',
            'price': '18.99',
            'is_veg': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(FoodItem.objects.filter(name='New Pizza').exists())

    def test_add_food_item_unauthenticated(self):
        """Test add food item for unauthenticated user"""
        response = self.client.post(reverse('add_food_item', args=[self.restaurant.id]), {
            'name': 'New Pizza',
            'description': 'A new pizza',
            'price': '18.99',
            'is_veg': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_edit_food_item_authenticated(self):
        """Test edit food item for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            price=Decimal('15.99')
        )
        response = self.client.post(reverse('edit_food_item', args=[food_item.id]), {
            'name': 'Updated Pizza',
            'description': 'An updated pizza',
            'price': '19.99',
            'is_veg': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        food_item.refresh_from_db()
        self.assertEqual(food_item.name, 'Updated Pizza')

    def test_delete_food_item_authenticated(self):
        """Test delete food item for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            price=Decimal('15.99')
        )
        response = self.client.post(reverse('delete_food_item', args=[food_item.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(FoodItem.objects.filter(id=food_item.id).exists())


class OrderManagementTests(TestCase):
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
            price=Decimal('15.99')
        )
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            total_price=Decimal('31.98'),
            status='Pending'
        )

    # def test_update_order_status_authenticated(self):
    #     """Test update order status for authenticated owner"""
    #     self.client.login(username='owner', password='testpass123')
    #     response = self.client.post(reverse('update_order_status', args=[self.order.id]), {
    #         'status': 'Confirmed'
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect after successful update
    #     self.order.refresh_from_db()
    #     self.assertEqual(self.order.status, 'Confirmed')

    # def test_update_order_status_unauthenticated(self):
    #     """Test update order status for unauthenticated user"""
    #     response = self.client.post(reverse('update_order_status', args=[self.order.id]), {
    #         'status': 'Confirmed'
    #     })
    #     self.assertEqual(response.status_code, 302)  # Redirect to login


class FeedbackManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.feedback = Feedback.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            feedback_type='complaint',
            message='Test feedback message'
        )

    def test_feedback_management_authenticated(self):
        """Test feedback management for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('feedback_management', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test feedback message')

    def test_feedback_management_unauthenticated(self):
        """Test feedback management for unauthenticated user"""
        response = self.client.get(reverse('feedback_management', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_respond_to_feedback_authenticated(self):
        """Test respond to feedback for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('respond_to_feedback', args=[self.feedback.id]), {
            'response': 'Thank you for your feedback'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful response
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.response, 'Thank you for your feedback')
        self.assertEqual(self.feedback.responded_by, self.owner)

    def test_mark_feedback_seen_authenticated(self):
        """Test mark feedback as seen for authenticated owner"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('mark_feedback_seen', args=[self.feedback.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.feedback.refresh_from_db()
        self.assertTrue(self.feedback.seen)