from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        User,
        related_name="restaurants",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        upload_to="restaurant_photos/", blank=True, null=True
    )
    location = models.CharField(max_length=150, blank=True, null=True)
    cuisine = models.CharField(max_length=150, blank=True, null=True)
    avg_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
        upload_to="food_images/", blank=True, null=True
    )
    is_veg = models.BooleanField(default=True)

    # New fields
    is_special = models.BooleanField(default=False)  # Flag for "Today's Special"
    deal_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )  # Discounted price
    deal_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    def get_display_price(self):
        """Return deal price if active, otherwise normal price."""
        if self.deal_active and self.deal_price:
            return self.deal_price
        return self.price


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="orders"
    )
    items = models.ManyToManyField(FoodItem, through="OrderItem")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Pending"
    )

    def __str__(self):
        return (
            f"Order {self.id} at {self.restaurant.name} "
            f"by {self.customer.username}"
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"


class UserProfile(models.Model):
    DIET_CHOICES = [
        ("any", "Any"),
        ("veg", "Vegetarian"),
        ("nonveg", "Non-Vegetarian"),
        ("vegan", "Vegan"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    diet_preference = models.CharField(
        max_length=20, choices=DIET_CHOICES, default="any"
    )
    cuisine_preference = models.CharField(max_length=200, blank=True)
    favorite_restaurants = models.ManyToManyField(
        Restaurant, blank=True, related_name="fans"
    )

    def __str__(self):
        return f"Profile: {self.user.username}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(default=5)  # 1..5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)  # Owner can hide if necessary

    def __str__(self):
        return (
            f"{self.rating} - {self.restaurant.name} "
            f"by {self.user.username}"
        )


class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ("complaint", "Complaint"),
        ("suggestion", "Suggestion"),
        ("compliment", "Compliment"),
        ("general", "General Feedback"),
    ]

    PRIORITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="feedbacks"
    )
    feedback_type = models.CharField(
        max_length=20, choices=FEEDBACK_TYPES, default="general"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    # Response fields (owner response)
    response = models.TextField(blank=True, null=True)
    responded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_responses",
    )
    responded_at = models.DateTimeField(blank=True, null=True)

    priority = models.CharField(
        max_length=10, choices=PRIORITY, default="medium"
    )

    def add_response(self, user, response_text):
        """Owner adds a response to the feedback."""
        self.response = response_text
        self.responded_by = user
        self.responded_at = timezone.now()
        self.seen = True
        self.save()

    def __str__(self):
        return f"Feedback for {self.restaurant.name} by {self.user.username}"
