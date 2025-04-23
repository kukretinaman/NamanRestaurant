from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, DetailView
from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse_lazy
from django.db.models import Q
from .models import FoodItem, Order, OrderItem


# User Authentication Views
class SignupView(FormView):
    template_name = "customer/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("menu")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class LoginView(FormView):
    template_name = "customer/login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("menu")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")


# Profile View
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "customer/profile.html"


# Order History View
class OrdersView(LoginRequiredMixin, ListView):
    template_name = "customer/orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by("-created_at")


# Cancel Order View
class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id, customer=request.user)
        if order.status == "Pending":
            order.delete()
            messages.success(request, "Order canceled successfully.")
        else:
            messages.error(request, "You cannot cancel this order.")
        return redirect("orders")


# Menu View with Filtering and Cart Display
class MenuView(LoginRequiredMixin, TemplateView):
    template_name = "customer/menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("search", "").strip()
        max_price = self.request.GET.get("max_price", "").strip()

        filters = Q()
        if search_query:
            filters &= Q(name__icontains=search_query) | Q(description__icontains=search_query)
        if max_price:
            filters &= Q(price__lte=float(max_price))

        context["food_items"] = FoodItem.objects.filter(filters)

        # Cart Retrieval
        cart = cache.get(f"cart_{self.request.user.id}", {})
        cart_items = []
        total_price = 0
        for item_id, quantity in cart.items():
            try:
                food = FoodItem.objects.get(id=item_id)
                cart_items.append({"food": food, "quantity": quantity})
                total_price += food.price * quantity
            except FoodItem.DoesNotExist:
                pass

        context.update({
            "cart_items": cart_items,
            "total_price": total_price,
            "search_query": search_query,
            "max_price": max_price,
        })
        return context


# Cart Management Views
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, food_id):
        quantity = int(request.POST.get("quantity", 1))
        cart = cache.get(f"cart_{request.user.id}", {})
        cart[str(food_id)] = cart.get(str(food_id), 0) + quantity
        cache.set(f"cart_{request.user.id}", cart, timeout=86400)
        return redirect("menu")

class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, food_id, action):
        cart = cache.get(f"cart_{request.user.id}", {})

        if str(food_id) in cart:
            if action == "increase":
                cart[str(food_id)] += 1
            elif action == "decrease":
                if cart[str(food_id)] > 1:
                    cart[str(food_id)] -= 1
                else:
                    del cart[str(food_id)]
            elif action == "remove":
                del cart[str(food_id)]

        cache.set(f"cart_{request.user.id}", cart, timeout=86400)
        return redirect("menu")

class ClearCartView(LoginRequiredMixin, View):
    def post(self, request):
        cache.delete(f"cart_{request.user.id}")
        return redirect("menu")


# Order Placement View
class PlaceOrderView(LoginRequiredMixin, View):
    def post(self, request):
        cart = cache.get(f"cart_{request.user.id}", {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect("menu")

        total_price = sum(FoodItem.objects.get(id=item_id).price * quantity for item_id, quantity in cart.items())
        order = Order.objects.create(customer=request.user, total_price=total_price)

        for item_id, quantity in cart.items():
            food_item = FoodItem.objects.get(id=item_id)
            OrderItem.objects.create(order=order, food_item=food_item, quantity=quantity)

        cache.delete(f"cart_{request.user.id}")
        messages.success(request, "Order placed successfully!")
        return redirect("orders")
