# Standard library
import json
import logging

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe

# Local imports
from customer.forms import FeedbackResponseForm, FoodItemForm
from customer.models import Feedback, FoodItem, Order, OrderItem, Restaurant


logger = logging.getLogger(__name__)

@login_required
def owner_dashboard(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    menu_items = restaurant.menu_items.all()
    orders = restaurant.orders.all().order_by('-created_at')
    feedbacks = restaurant.feedbacks.all().order_by('-created_at')

    # Insights: only completed orders
    completed_orders = restaurant.orders.filter(status='Completed')
    total_sales = completed_orders.aggregate(total=Sum('total_price'))['total'] or 0
    total_orders = completed_orders.count()
    total_items = menu_items.count()
    pending_orders = restaurant.orders.filter(status='Pending').count()

    # Sales over time
    sales_data = completed_orders.values('created_at__date').annotate(
        total=Sum('total_price')
    ).order_by('created_at__date')
    sales_labels = [str(s['created_at__date']) for s in sales_data]
    sales_values = [float(s['total'] or 0) for s in sales_data]

    # Top ordered items
    top_items_qs = OrderItem.objects.filter(
        order__in=completed_orders
    ).values('food_item__name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:6]
    items_labels = [i['food_item__name'] for i in top_items_qs]
    items_values = [i['total_qty'] for i in top_items_qs]

    # Top customers
    top_customers_qs = completed_orders.values('customer__username').annotate(
        total_spent=Sum('total_price')
    ).order_by('-total_spent')[:6]
    customers_labels = [c['customer__username'] for c in top_customers_qs]
    customers_values = [float(c['total_spent']) for c in top_customers_qs]

    # Handle profile update
    if request.method == "POST" and 'update_profile' in request.POST:
        restaurant.name = request.POST.get('name')
        restaurant.description = request.POST.get('description')
        restaurant.cuisine = request.POST.get("cuisine")
        restaurant.location = request.POST.get("location")
        restaurant.avg_price = request.POST.get("avg_price")
        restaurant.phone = request.POST.get("phone")
        if 'photo' in request.FILES:
            restaurant.photo = request.FILES['photo']
        restaurant.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('owner_dashboard', restaurant_id=restaurant.id)

    return render(request, 'system/owner_dashboard.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'orders': orders,
        'feedbacks': feedbacks,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_items': total_items,
        'pending_orders': pending_orders,
        'sales_labels': sales_labels,
        'sales_values': sales_values,
        'items_labels': items_labels,
        'items_values': items_values,
        'customers_labels': customers_labels,
        'customers_values': customers_values,
    })


@login_required
def add_food_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.restaurant = restaurant
            food_item.save()
            messages.success(request, f"Food item '{food_item.name}' added successfully!")
            logger.info("Food item %s added by %s", food_item.id, request.user.username)
            return redirect('owner_dashboard', restaurant_id=restaurant.id)
        else:
            messages.error(request, "Failed to add food item. Please check the form.")
    else:
        form = FoodItemForm()
    return render(request, 'system/add_food_item.html', {'form': form, 'restaurant': restaurant})

@login_required
def edit_food_item(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    if food.restaurant.owner != request.user:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, f"Food item '{food.name}' updated successfully!")
            logger.info("Food item %s updated by %s", food.id, request.user.username)
            return redirect('owner_dashboard', restaurant_id=food.restaurant.id)
        else:
            messages.error(request, "Failed to update food item. Please check the form.")
    else:
        form = FoodItemForm(instance=food)
    return render(request, 'system/edit_food_item.html', {'form': form, 'food': food})

@login_required
def delete_food_item(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)
    if food.restaurant.owner != request.user:
        return HttpResponseForbidden()
    restaurant_id = food.restaurant.id
    food_name = food.name
    food.delete()
    messages.success(request, f"Food item '{food_name}' deleted successfully!")
    logger.info("Food item %s deleted by %s", food_id, request.user.username)
    return redirect('owner_dashboard', restaurant_id=restaurant_id)

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.restaurant.owner != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()
    # status comes from POST (if form) else toggle or a default flow
    if request.method == "POST":
        old_status = order.status
        new_status = request.POST.get('status')
        if new_status in ["Pending", "Completed", "Cancelled"]:
            order.status = new_status
            order.save()
            if old_status != new_status:
                messages.success(request, f"Order #{order.id} status changed from {old_status} to {new_status}")
                logger.info("Order %s status changed to %s by %s", order.id, new_status, request.user.username)
    else:
        # quick toggle: Pending -> Completed
        old_status = order.status
        if order.status == 'Pending':
            order.status = 'Completed'
        else:
            order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} status changed from {old_status} to {order.status}")
    return redirect(request.META.get("HTTP_REFERER", "owner_dashboard"))

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.restaurant.owner != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()
    rest_id = order.restaurant.id
    order_id = order.id
    order.delete()
    messages.success(request, f"Order #{order_id} deleted successfully!")
    return redirect('owner_dashboard', restaurant_id=rest_id)

@login_required
def insights_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    completed_orders = restaurant.orders.filter(status="Completed")

    total_sales = completed_orders.aggregate(total=Sum("total_price"))["total"] or 0
    total_orders = completed_orders.count()
    menu_items = restaurant.menu_items.count()

    # Sales over time (only completed)
    sales_data = (
        completed_orders
        .values("created_at__date")
        .annotate(total=Sum("total_price"))
        .order_by("created_at__date")
    )

    # Top items (only completed)
    top_items = (
        OrderItem.objects
        .filter(order__in=completed_orders)
        .values("food_item__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    return render(request, "system/insights.html", {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "menu_items": menu_items,
        "sales_data": sales_data,
        "top_items": top_items,
    })

@login_required
def feedback_management(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    feedbacks = restaurant.feedbacks.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'unseen':
        feedbacks = feedbacks.filter(seen=False)
    elif status_filter == 'responded':
        feedbacks = feedbacks.exclude(response__isnull=True).exclude(response='')
    elif status_filter == 'pending':
        feedbacks = feedbacks.filter(response__isnull=True)
    
    # Filter by type
    type_filter = request.GET.get('type', 'all')
    if type_filter != 'all':
        feedbacks = feedbacks.filter(feedback_type=type_filter)
    
    return render(request, 'system/feedback_management.html', {
        'restaurant': restaurant,
        'feedbacks': feedbacks,
        'status_filter': status_filter,
        'type_filter': type_filter,
    })

@login_required
def respond_to_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if feedback.restaurant.owner != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = FeedbackResponseForm(request.POST)
        if form.is_valid():
            response_text = form.cleaned_data['response']
            # Assign the response text
            feedback.response = response_text
            # Assign the owner who responded
            feedback.responded_by = request.user
            # Record the response time
            from django.utils import timezone
            feedback.responded_at = timezone.now()
            # Mark as seen
            feedback.seen = True

            feedback.save()
            messages.success(request, f"Response sent to {feedback.user.username}")
            return redirect('feedback_management', restaurant_id=feedback.restaurant.id)
    else:
        form = FeedbackResponseForm()
    
    return render(request, 'system/respond_feedback.html', {
        'feedback': feedback,
        'form': form,
    })

@login_required
def mark_feedback_seen(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if feedback.restaurant.owner != request.user:
        return HttpResponseForbidden()
    
    feedback.seen = True
    feedback.save()
    messages.success(request, "Feedback marked as seen")
    return redirect('feedback_management', restaurant_id=feedback.restaurant.id)

def insights(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Only completed orders count as revenue
    completed_orders = restaurant.orders.filter(status="Completed")

    # Total revenue
    revenue = completed_orders.aggregate(total=Sum('total_price'))['total'] or 0

    # Top ordered items
    top_items = OrderItem.objects.filter(
        order__status="Completed", 
        food_item__restaurant=restaurant
    ).values(
        "food_item__name"
    ).annotate(
        total_quantity=Sum("quantity")
    ).order_by("-total_quantity")[:5]

    # Top customers
    top_customers = completed_orders.values(
        "customer__username"
    ).annotate(
        total_spent=Sum("total_price")
    ).order_by("-total_spent")[:5]

    return render(request, "system/insights.html", {
        "restaurant": restaurant,
        "revenue": revenue,
        "top_items": top_items,
        "top_customers": top_customers,
    })