# Standard library
import logging
from decimal import Decimal

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.db import transaction, models
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, Count
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

# Local imports
from .models import Restaurant, FoodItem, Order, OrderItem, Review, Feedback, UserProfile
from .forms import RegisterRestaurantForm, ReviewForm, FeedbackForm, FeedbackResponseForm, UserProfileForm, FoodItemForm


logger = logging.getLogger(__name__)

# ---------- Auth ----------
class SignupView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        # validations
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        # create user
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, phone=phone)

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        # allow login with either username or email
        try:
            user_obj = User.objects.get(email=username_or_email)
            username = user_obj.username
        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # If owner, go to their first restaurant dashboard
            owner_rests = getattr(user, "restaurants", None)
            if owner_rests and owner_rests.exists():
                logger.info("Owner %s logged in", user.username)
                first_rest = owner_rests.first()
                return redirect("owner_dashboard", restaurant_id=first_rest.id)

            logger.info("Customer %s logged in", user.username)
            return redirect("restaurant_list")

        messages.error(request, "Invalid username/email or password.")
        return render(request, "login.html")

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')

# ---------- Restaurant list + search ----------
class RestaurantListView(View):
    def get(self, request):
        from django.db.models import Avg, Count
        
        logger.info(f"Restaurant list accessed by user: {request.user}")
        
        qs = Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('name')
        q = request.GET.get('q','').strip()
        cuisine = request.GET.get('cuisine','').strip()
        location = request.GET.get('location','').strip()
        max_price = request.GET.get('price','').strip()
        page = request.GET.get('page', 1)

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
            logger.info(f"Restaurant search performed: '{q}' by user {request.user}")
        if cuisine:
            qs = qs.filter(cuisine__icontains=cuisine)
            logger.info(f"Restaurant filtered by cuisine: '{cuisine}'")
        if location:
            qs = qs.filter(location__icontains=location)
            logger.info(f"Restaurant filtered by location: '{location}'")
        if max_price:
            try:
                from decimal import Decimal
                qs = qs.filter(avg_price__lte=Decimal(max_price))
                logger.info(f"Restaurant filtered by max price: ₹{max_price}")
            except Exception as e:
                logger.warning(f"Invalid price filter provided: '{max_price}' - {str(e)}")

        # pagination (page size 3 so 3x3 grid)
        paginator = Paginator(qs, 6)
        restaurants_page = paginator.get_page(page)

        # recommended (simple heuristic)
        recommended = []
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                if profile.cuisine_preference:
                    recommended = list(Restaurant.objects.filter(cuisine__icontains=profile.cuisine_preference).annotate(
                        avg_rating=Avg('reviews__rating'),
                        review_count=Count('reviews')
                    )[:6])
                if profile.favorite_restaurants.exists():
                    for r in profile.favorite_restaurants.all().annotate(
                        avg_rating=Avg('reviews__rating'),
                        review_count=Count('reviews')
                    )[:6]:
                        if r not in recommended:
                            recommended.append(r)

        return render(request, 'restaurant_list.html', {
            'restaurants': restaurants_page,    # page object used by template
            'recommended': recommended,
            'q': q,
            'cuisine': cuisine,
            'location': location,
            'max_price': max_price,
        })

# ---------- Menu ----------
class MenuView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        search_query = request.GET.get('search', '')
        max_price = request.GET.get('max_price','')
        veg_filter = request.GET.get('veg','')

        items = restaurant.menu_items.all().order_by(
            models.Case(
                models.When(is_special=True, then=0),
                models.When(deal_active=True, then=1),
                default=2,
                output_field=models.IntegerField(),
            ),
            'id'
        )
        if search_query:
            items = items.filter(name__icontains=search_query)
        if max_price:
            try:
                max_p = Decimal(max_price)
                items = items.filter(price__lte=max_p)
            except:
                pass
        if veg_filter == 'veg':
            items = items.filter(is_veg=True)
        elif veg_filter == 'nonveg':
            items = items.filter(is_veg=False)

        # Popular today (>10)
        from django.utils.timezone import now
        today = now().date()
        popular_qs = OrderItem.objects.filter(
            food_item__restaurant=restaurant,
            order__created_at__date=today
        ).values("food_item__id","food_item__name").annotate(total=Sum("quantity")).filter(total__gt=10)
        popular_items = [p['food_item__id'] for p in popular_qs]

        # pagination
        from django.core.paginator import Paginator
        paginator = Paginator(items, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # cart
        cart_key = f'cart_{restaurant_id}'
        cart = request.session.get(cart_key, {})
        cart_items = []
        total_price = Decimal('0')
        for fid, qty in cart.items():
            try:
                food = FoodItem.objects.get(id=int(fid), restaurant=restaurant)
                subtotal = food.get_display_price() * qty
                cart_items.append({
                    'food': food, 
                    'quantity': qty, 
                    'subtotal': subtotal
                })
                total_price += subtotal
            except FoodItem.DoesNotExist:
                continue

        # reviews
        reviews = restaurant.reviews.filter(visible=True).order_by('-created_at')[:10]

        # whether user can review (completed order exists)
        has_completed_order = False
        if request.user.is_authenticated:
            has_completed_order = Order.objects.filter(
                customer=request.user,
                restaurant=restaurant,
                status='Completed'
            ).exists()

        return render(request, 'menu.html', {
            'restaurant': restaurant,
            'page_obj': page_obj,
            'cart_items': cart_items,
            'total_price': total_price,
            'search_query': search_query,
            'max_price': max_price,
            'veg_filter': veg_filter,
            'popular_items': popular_items,
            'reviews': reviews,
            'review_form': ReviewForm(),
            'feedback_form': FeedbackForm(),
            'can_review': has_completed_order,
        })

# ---------- Cart and Order ----------
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id, food_id):
        _ = get_object_or_404(Restaurant, id=restaurant_id)
        food = get_object_or_404(FoodItem, id=food_id, restaurant_id=restaurant_id)
        qty = int(request.POST.get('quantity',1))
        cart_key = f'cart_{restaurant_id}'
        cart = request.session.get(cart_key, {})
        cart[str(food.id)] = cart.get(str(food.id), 0) + max(1, qty)
        request.session[cart_key] = cart
        messages.success(request, f"Added {food.name} to cart")
        return redirect('menu', restaurant_id=restaurant_id)

class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id, food_id, action):
        _ = get_object_or_404(Restaurant, id=restaurant_id)
        food = get_object_or_404(FoodItem, id=food_id, restaurant_id=restaurant_id)
        cart_key = f'cart_{restaurant_id}'
        cart = request.session.get(cart_key, {})
        fid = str(food.id)
        if action == 'increase':
            cart[fid] = cart.get(fid,0) + 1
        elif action == 'decrease':
            if cart.get(fid,0) > 1:
                cart[fid] -= 1
            else:
                cart.pop(fid, None)
        elif action == 'remove':
            cart.pop(fid, None)
        request.session[cart_key] = cart
        return redirect('menu', restaurant_id=restaurant_id)

class ClearCartView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):
        request.session.pop(f'cart_{restaurant_id}', None)
        messages.success(request, "Cart cleared")
        return redirect('menu', restaurant_id=restaurant_id)

class PlaceOrderView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        cart_key = f'cart_{restaurant_id}'
        cart = request.session.get(cart_key, {})
        if not cart:
            messages.error(request, "Cart empty")
            return redirect('menu', restaurant_id=restaurant_id)

        total = Decimal('0')
        items_data = []
        for fid, qty in cart.items():
            food = get_object_or_404(FoodItem, id=int(fid), restaurant=restaurant)
            items_data.append((food, qty))
            total += food.price * qty

        order = Order.objects.create(customer=request.user, restaurant=restaurant, total_price=total)
        for food, qty in items_data:
            OrderItem.objects.create(order=order, food_item=food, quantity=qty)
        request.session.pop(cart_key, None)
        messages.success(request, f"Order placed successfully (#{order.id})")
        
        # redirect to friendly orders
        return redirect('orders')

# ---------- Orders views ----------
class OrdersView(LoginRequiredMixin, View):
    def get(self, request, restaurant_id=None):
        qs = Order.objects.filter(customer=request.user).order_by('-created_at')

        # 🔍 Search
        q = request.GET.get('search', '').strip()
        if q:
            qs = qs.filter(
                Q(id__icontains=q) |
                Q(restaurant__name__icontains=q) |
                Q(items__name__icontains=q)
            ).distinct()

        # pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(qs, 6)
        orders_page = paginator.get_page(page)

        return render(request, 'orders.html', {
            'orders': orders_page,
            'search': q,
        })


class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status == 'Pending':
            order.status = 'Cancelled'
            order.save()
            messages.success(request, "Order cancelled")
        else:
            messages.error(request, "Cannot cancel")
        return redirect('orders')

# ---------- Profile ----------
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(instance=profile)
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')[:10]
        all_restaurants = Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('name')
        return render(request, 'profile.html', {
            'form': form,
            'profile': profile,
            'orders': orders,
            'feedbacks': feedbacks,
            'all_restaurants': all_restaurants,
        })

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect('profile')
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')[:10]
        all_restaurants = Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('name')
        return render(request, 'profile.html', {
            'form': form,
            'profile': profile,
            'orders': orders,
            'feedbacks': feedbacks,
            'all_restaurants': all_restaurants,
        })

# ---------- Register Restaurant ----------
class RegisterRestaurantView(LoginRequiredMixin, View):
    def get(self, request):
        form = RegisterRestaurantForm()
        return render(request, 'register_restaurant.html', {'form': form})

    def post(self, request):
        form = RegisterRestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            rest = form.save(commit=False)
            rest.owner = request.user
            rest.save()
            messages.success(request, "Restaurant registered; you can manage it from Dashboard")
            return redirect('owner_dashboard', restaurant_id=rest.id)
        return render(request, 'register_restaurant.html', {'form': form})

# ---------- Reviews & Feedback ----------
class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        # gate: user must have at least one completed order at this restaurant
        has_completed = Order.objects.filter(customer=request.user, restaurant=restaurant, status='Completed').exists()
        if not has_completed:
            messages.error(request, "You can review after completing an order at this restaurant.")
            return redirect('menu', restaurant_id=restaurant.id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.user = request.user
            rev.restaurant = restaurant
            rev.save()
            logger.info("Review added by %s for restaurant %s (rating=%s)", 
                request.user.username, 
                restaurant.id, 
                rev.rating
            )
            messages.success(request, "Thanks for your review!")
        else:
            messages.error(request, "Invalid review")
        return redirect('menu', restaurant_id=restaurant.id)

class AddFeedbackView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            fb.restaurant = restaurant
            fb.save()
            logger.info("Feedback added by %s for restaurant %s", request.user.username, restaurant.id)
            messages.success(request, "Feedback submitted successfully! Restaurant will review and respond.")
        else:
            messages.error(request, "Invalid feedback")
        return redirect('menu', restaurant_id=restaurant.id)

class CustomerFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'customer/feedback_history.html', {'feedbacks': feedbacks})


class PasswordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'customer/password_change.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully")
            return render(request, 'profile.html')
        messages.error(request, "Please correct the errors below.")
        return render(request, 'customer/password_change.html', {'form': form})
