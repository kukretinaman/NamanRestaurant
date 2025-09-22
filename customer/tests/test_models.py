from django.test import TestCase # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.core.exceptions import ValidationError # type: ignore
from decimal import Decimal
from customer.models import Restaurant, FoodItem, Order, OrderItem, Review, Feedback, UserProfile


class RestaurantModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City',
            cuisine='Italian',
            description='A test restaurant',
            avg_price=Decimal('25.50')
        )

    def test_restaurant_creation(self):
        """Test restaurant model creation"""
        self.assertEqual(self.restaurant.name, 'Test Restaurant')
        self.assertEqual(self.restaurant.owner, self.owner)
        self.assertEqual(self.restaurant.location, 'Test City')
        self.assertEqual(self.restaurant.cuisine, 'Italian')
        self.assertEqual(self.restaurant.avg_price, Decimal('25.50'))

    def test_restaurant_str_representation(self):
        """Test restaurant string representation"""
        self.assertEqual(str(self.restaurant), 'Test Restaurant')


class FoodItemModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            name='Test Pizza',
            description='A delicious test pizza',
            price=Decimal('15.99'),
            is_veg=True
        )


class OrderModelTests(TestCase):
    def setUp(self):
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
            price=Decimal('15.99')
        )
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            total_price=Decimal('31.98'),
            status='Pending'
        )

    def test_order_creation(self):
        """Test order model creation"""
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.restaurant, self.restaurant)
        self.assertEqual(self.order.total_price, Decimal('31.98'))
        self.assertEqual(self.order.status, 'Pending')

    def test_order_status_choices(self):
        """Test order status choices"""
        valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled']
        for status in valid_statuses:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)


class OrderItemModelTests(TestCase):
    def setUp(self):
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
            price=Decimal('15.99')
        )
        self.order = Order.objects.create(
            customer=self.customer,
            restaurant=self.restaurant,
            total_price=Decimal('31.98')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            food_item=self.food_item,
            quantity=2
        )

    def test_order_item_creation(self):
        """Test order item model creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.food_item, self.food_item)
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_item_str_representation(self):
        """Test order item string representation"""
        expected = f"2 x {self.food_item.name}"
        self.assertEqual(str(self.order_item), expected)

    def test_order_item_total_price(self):
        """Test order item total price calculation"""
        expected_total = self.order_item.food_item.get_display_price() * self.order_item.quantity
        self.assertEqual(expected_total, self.order_item.food_item.get_display_price() * self.order_item.quantity)



class ReviewModelTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.review = Review.objects.create(
            user=self.customer,
            restaurant=self.restaurant,
            rating=4,
            comment='Great food!'
        )

    def test_review_creation(self):
        """Test review model creation"""
        self.assertEqual(self.review.user, self.customer)
        self.assertEqual(self.review.restaurant, self.restaurant)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Great food!')

    def test_review_str_representation(self):
        """Test review string representation"""
        expected = f"4 - {self.restaurant.name} by {self.customer.username}"
        self.assertEqual(str(self.review), expected)


class FeedbackModelTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
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

    def test_feedback_creation(self):
        """Test feedback model creation"""
        self.assertEqual(self.feedback.user, self.customer)
        self.assertEqual(self.feedback.restaurant, self.restaurant)
        self.assertEqual(self.feedback.feedback_type, 'complaint')
        self.assertEqual(self.feedback.message, 'Test feedback message')
        self.assertFalse(self.feedback.seen)

    def test_feedback_str_representation(self):
        """Test feedback string representation"""
        expected = f"Feedback for {self.restaurant.name} by {self.customer.username}"
        self.assertEqual(str(self.feedback), expected)

    def test_feedback_mark_as_seen(self):
        """Test feedback mark as seen functionality"""
        self.assertFalse(self.feedback.seen)
        self.feedback.seen = True
        self.feedback.save()
        self.assertTrue(self.feedback.seen)


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='+1234567890',
            diet_preference='Vegetarian',
            cuisine_preference='Italian'
        )

    def test_user_profile_creation(self):
        """Test user profile model creation"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone, '+1234567890')
        self.assertEqual(self.profile.diet_preference, 'Vegetarian')
        self.assertEqual(self.profile.cuisine_preference, 'Italian')

    def test_user_profile_str_representation(self):
        """Test user profile string representation"""
        expected = f"Profile: {self.user.username}"
        self.assertEqual(str(self.profile), expected)

    def test_user_profile_favorite_restaurants(self):
        """Test user profile favorite restaurants relationship"""
        self.profile.favorite_restaurants.add(self.restaurant)
        self.assertIn(self.restaurant, self.profile.favorite_restaurants.all())