import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import (
    Restaurant,
    FoodItem,
    Order,
    OrderItem,
    Review,
    Feedback,
    UserProfile,
)

admin.site.site_header = "Naman Restaurant Admin Panel"
admin.site.site_title = "Restaurant Management"
admin.site.index_title = "Welcome to the Dashboard"


def download_csv(modeladmin, request, queryset):
    """Custom admin action to download selected food items as CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="food_items.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Description", "Price", "Restaurant"])

    for item in queryset:
        writer.writerow([
            item.id,
            item.name,
            item.description,
            item.price,
            getattr(item.restaurant, "name", ""),
        ])
    return response


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "restaurant", "description")
    list_filter = ("price", "restaurant")
    search_fields = ("name", "description", "restaurant__name")
    ordering = ("id",)
    actions = [download_csv]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant__owner=request.user)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("food_item", "quantity")
    readonly_fields = ("food_item",)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "restaurant",
        "total_price",
        "status",
        "ordered_items",
        "created_at",
    )
    list_filter = ("status", "created_at", "restaurant")
    search_fields = ("customer__username", "status", "restaurant__name")
    ordering = ("-created_at",)
    list_editable = ("status",)
    inlines = [OrderItemInline]

    def ordered_items(self, obj):
        items = obj.orderitem_set.all()
        return ", ".join(
            [f"{item.food_item.name} (x{item.quantity})" for item in items]
        )

    ordered_items.short_description = "Ordered Items"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant__owner=request.user)


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review)
admin.site.register(Feedback)
admin.site.register(UserProfile)
