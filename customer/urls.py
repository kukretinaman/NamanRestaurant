from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("menu/", MenuView.as_view(), name="menu"),
    path("orders/", OrdersView.as_view(), name="orders"),
    path("profile/", ProfileView.as_view(), name="profile"),

    path("orders/cancel/<int:order_id>/", CancelOrderView.as_view(), name="cancel_order"),
    path("add_to_cart/<int:food_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/update/<int:food_id>/<str:action>/", UpdateCartView.as_view(), name="update_cart"),
    path("clear_cart/", ClearCartView.as_view(), name="clear_cart"),
    path("place_order/", PlaceOrderView.as_view(), name="place_order"),
]
