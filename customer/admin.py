import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import FoodItem, Order, OrderItem

#change Django admin site specifications
admin.site.site_header = "Naman Restaurant Admin Panel"
admin.site.site_title = "Restaurant Management"
admin.site.index_title = "Welcome to the Dashboard"

#csv download
def download_csv(*_, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="food_items.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Description", "Price"])  #CSV Headers

    for item in queryset:
        writer.writerow([item.id, item.name, item.description, item.price])  #CSV Data

    return response

#admin actions
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "description")  #columns in admin panel
    list_filter = ("price",)  #add price filter
    search_fields = ("name", "description")  #enable search in admin panel
    ordering = ("id",)  #sort by ID by default
    actions = [download_csv]  #register the admin action

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("food_item", "quantity")  # Allow editing of food items and quantity
    readonly_fields = ("food_item",)  # Make food item non-editable but allow quantity changes

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "total_price", "status", "ordered_items", "created_at",)
    list_filter = ("status", "created_at",)
    search_fields = ("customer__username", "status",)
    ordering = ("-created_at",)
    list_editable = ("status",)
    inlines = [OrderItemInline]

    def ordered_items(self, obj):
        """Return a formatted list of ordered items"""
        items = obj.orderitem_set.all()
        return ", ".join([f"{item.food_item.name} (x{item.quantity})" for item in items])
    
    ordered_items.short_description = "Ordered Items"


admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Order, OrderAdmin)
