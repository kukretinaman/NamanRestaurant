from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/<int:restaurant_id>/", views.owner_dashboard, name="owner_dashboard"),
    path("food/add/<int:restaurant_id>/", views.add_food_item, name="add_food_item"),
    path("food/<int:food_id>/edit/", views.edit_food_item, name="edit_food_item"),
    path("food/<int:food_id>/delete/", views.delete_food_item, name="delete_food_item"),
    path("order/<int:order_id>/update/", views.update_order_status, name="update_order_status"),
    path("order/<int:order_id>/delete/", views.delete_order, name="delete_order"),
    path("feedback/<int:restaurant_id>/", views.feedback_management, name="feedback_management"),
    path("feedback/respond/<int:feedback_id>/", views.respond_to_feedback, name="respond_to_feedback"),
    path("feedback/mark-seen/<int:feedback_id>/", views.mark_feedback_seen, name="mark_feedback_seen"),
]
