from django.contrib import admin
from .models import (
    Product,
    CartItem,
    Order,
    OrderItem,
    ContactMessage,
    Newsletter,
    BlogPost,
    Review,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "size", "quantity", "price")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "category", "featured", "new_arrival")
    list_filter = ("category", "featured", "new_arrival")
    search_fields = ("name", "brand")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "email",
        "total",
        "payment_method",
        "payment_status",
        "created_at",
    )
    list_filter = ("payment_method", "payment_status", "created_at")
    search_fields = ("customer_name", "email")
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "posted_on")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("session_key", "product", "quantity", "size")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "body")
    readonly_fields = ("created_at", "updated_at")
