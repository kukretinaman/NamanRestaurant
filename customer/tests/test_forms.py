from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from customer.forms import UserProfileForm, FeedbackForm, ReviewForm, RegisterRestaurantForm, FoodItemForm
from customer.models import Restaurant, UserProfile


class UserProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='+1234567890',
            diet_preference='Vegetarian',
            cuisine_preference='Italian'
        )

    def test_user_profile_form_valid_data(self):
        """Test user profile form with valid data"""
        form_data = {
            'phone': '+9876543210',
            'diet_preference': 'vegan',
            'cuisine_preference': 'Indian'
        }
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_user_profile_form_empty_data(self):
        """Test user profile form with empty data"""
        form = UserProfileForm(data={})
        self.assertFalse(form.is_valid())


class FeedbackFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )

    def test_feedback_form_valid_data(self):
        """Test feedback form with valid data"""
        form_data = {
            'feedback_type': 'complaint',
            'message': 'Test feedback message'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_feedback_form_empty_message(self):
        """Test feedback form with empty message"""
        form_data = {
            'feedback_type': 'complaint',
            'message': ''
        }
        form = FeedbackForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_feedback_form_invalid_feedback_type(self):
        """Test feedback form with invalid feedback type"""
        form_data = {
            'feedback_type': 'invalid_type',
            'message': 'Test feedback message'
        }
        form = FeedbackForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('feedback_type', form.errors)


class ReviewFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )

    def test_review_form_valid_data(self):
        """Test review form with valid data"""
        form_data = {
            'rating': 5,
            'comment': 'Great food!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())


class RegisterRestaurantFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_register_restaurant_form_valid_data(self):
        """Test register restaurant form with valid data"""
        form_data = {
            'name': 'Test Restaurant',
            'location': 'Test City',
            'cuisine': 'Italian',
            'description': 'A test restaurant',
            'avg_price': '25.50'
        }
        form = RegisterRestaurantForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_restaurant_form_empty_name(self):
        """Test register restaurant form with empty name"""
        form_data = {
            'name': '',
            'location': 'Test City',
            'cuisine': 'Italian',
            'description': 'A test restaurant',
            'avg_price': '25.50'
        }
        form = RegisterRestaurantForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_register_restaurant_form_invalid_price(self):
        """Test register restaurant form with invalid price"""
        form_data = {
            'name': 'Test Restaurant',
            'location': 'Test City',
            'cuisine': 'Italian',
            'description': 'A test restaurant',
            'avg_price': 'invalid_price'
        }
        form = RegisterRestaurantForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('avg_price', form.errors)


class FoodItemFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            owner=self.owner,
            location='Test City'
        )

    def test_food_item_form_valid_data(self):
        """Test food item form with valid data"""
        form_data = {
            'name': 'Test Pizza',
            'description': 'A delicious pizza',
            'price': '15.99',
            'is_veg': True,
            'deal_price': '12.99',
            'deal_active': True
        }
        form = FoodItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_food_item_form_empty_name(self):
        """Test food item form with empty name"""
        form_data = {
            'name': '',
            'description': 'A delicious pizza',
            'price': '15.99',
            'is_veg': True
        }
        form = FoodItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_food_item_form_invalid_price(self):
        """Test food item form with invalid price"""
        form_data = {
            'name': 'Test Pizza',
            'description': 'A delicious pizza',
            'price': 'invalid_price',
            'is_veg': True
        }
        form = FoodItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_food_item_form_deal_price_validation(self):
        """Test food item form deal price validation"""
        form_data = {
            'name': 'Test Pizza',
            'description': 'A delicious pizza',
            'price': '15.99',
            'is_veg': True,
            'deal_price': '20.00',  # Deal price higher than regular price
            'deal_active': True
        }
        form = FoodItemForm(data=form_data)
        # This should be valid as we're not enforcing deal price < regular price in the form
        self.assertTrue(form.is_valid())