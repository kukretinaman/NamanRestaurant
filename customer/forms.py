from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from .models import (
    UserProfile,
    Restaurant,
    Review,
    Feedback,
    FoodItem,
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "diet_preference",
            "cuisine_preference",
            "favorite_restaurants",
        ]
        widgets = {
            # Switch to a searchable multi-select dropdown
            "favorite_restaurants": forms.SelectMultiple(
                attrs={"class": "form-select"}
            ),
        }


class RegisterRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "name",
            "description",
            "photo",
            "location",
            "cuisine",
            "avg_price",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "photo": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "cuisine": forms.TextInput(attrs={"class": "form-control"}),
            "avg_price": forms.NumberInput(attrs={"class": "form-control"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["feedback_type", "message"]
        widgets = {
            "feedback_type": forms.Select(
                attrs={"class": "form-control"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Share your experience, suggestions, "
                        "or concerns..."
                    ),
                }
            ),
        }


class FeedbackResponseForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Type your response to the customer...",
            }
        ),
        required=True,
    )


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = [
            "name",
            "description",
            "price",
            "image",
            "is_veg",
            "is_special",
            "deal_price",
            "deal_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "is_veg": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "is_special": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "deal_price": forms.NumberInput(attrs={"class": "form-control"}),
            "deal_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
