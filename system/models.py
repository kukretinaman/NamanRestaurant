from django.db import models
from customer.models import Order, OrderItem, Restaurant

class OrderInsights:
    @staticmethod
    def total_revenue(restaurant):
        return Order.objects.filter(restaurant=restaurant).aggregate(models.Sum("total_price"))["total_price__sum"] or 0

    @staticmethod
    def most_ordered_items(restaurant):
        return (
            OrderItem.objects.filter(food_item__restaurant=restaurant)
            .values("food_item__name")
            .annotate(total_quantity=models.Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

    @staticmethod
    def top_customers(restaurant):
        return (
            Order.objects.filter(restaurant=restaurant)
            .values("customer__username")
            .annotate(total_spent=models.Sum("total_price"))
            .order_by("-total_spent")[:5]
        )
