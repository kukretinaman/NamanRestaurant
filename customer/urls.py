from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # Restaurants
    path(
        "restaurants/",
        views.RestaurantListView.as_view(),
        name="restaurant_list",
    ),
    path(
        "restaurant/<int:restaurant_id>/menu/",
        views.MenuView.as_view(),
        name="menu",
    ),

    # Orders
    path("orders/", views.OrdersView.as_view(), name="orders"),
    # Backward-compatible route
    path(
        "restaurant/<int:restaurant_id>/orders/",
        views.OrdersView.as_view(),
        name="orders_by_restaurant",
    ),
    path(
        "orders/cancel/<int:order_id>/",
        views.CancelOrderView.as_view(),
        name="cancel_order",
    ),

    # Cart
    path(
        "add_to_cart/<int:restaurant_id>/<int:food_id>/",
        views.AddToCartView.as_view(),
        name="add_to_cart",
    ),
    path(
        "cart/update/<int:restaurant_id>/<int:food_id>/<str:action>/",
        views.UpdateCartView.as_view(),
        name="update_cart",
    ),
    path(
        "clear_cart/<int:restaurant_id>/",
        views.ClearCartView.as_view(),
        name="clear_cart",
    ),
    path(
        "place_order/<int:restaurant_id>/",
        views.PlaceOrderView.as_view(),
        name="place_order",
    ),

    # Profile & account
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "password_change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="customer/password_change_done.html"
        ),
        name="password_change_done",
    ),

    # Register restaurant
    path(
        "register-restaurant/",
        views.RegisterRestaurantView.as_view(),
        name="register_restaurant",
    ),

    # Reviews & feedback
    path(
        "restaurant/<int:restaurant_id>/review/",
        views.AddReviewView.as_view(),
        name="add_review",
    ),
    path(
        "restaurant/<int:restaurant_id>/feedback/",
        views.AddFeedbackView.as_view(),
        name="add_feedback",
    ),
    path(
        "my-feedback/",
        views.CustomerFeedbackView.as_view(),
        name="customer_feedback",
    ),
]
