from django.db import models
from django.contrib.auth.models import User
from customer.models import Order, OrderItem, FoodItem

class OrderInsights:
    @staticmethod
    def total_revenue():
        return Order.objects.aggregate(models.Sum("total_price"))["total_price__sum"] or 0

    @staticmethod
    def most_ordered_items():
        return (
            OrderItem.objects.values(
                "food_item__name",
                )
            .annotate(total_quantity=models.Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

    @staticmethod
    def top_customers():
        return (
            Order.objects.values("customer__username")
            .annotate(total_spent=models.Sum("total_price"))
            .order_by("-total_spent")[:5]
        )
