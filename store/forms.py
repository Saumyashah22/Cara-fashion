from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "body")
        widgets = {
            "rating": forms.Select(attrs={"class": "review-rating-select"}),
            "body": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 1000,
                    "placeholder": "Share what you think about this product...",
                }
            ),
        }
        labels = {
            "rating": "Your rating",
            "body": "Your review",
        }

