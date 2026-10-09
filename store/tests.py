from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Order, OrderItem, Product, Review


class CheckoutTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="checkout-user",
            password="test-password-123",
        )
        self.client.force_login(self.user)
        self.product = Product.objects.create(
            brand="Cara",
            name="Test shirt",
            price="125.50",
            image="img/test.jpg",
            category="Shirt",
            description="Checkout test product",
        )
        self.client.post(
            reverse("add_to_cart", args=[self.product.pk]),
            {"quantity": "2", "size": "M"},
        )
        self.client.post(
            reverse("checkout"),
            {
                "customer_name": "Test Buyer",
                "email": "buyer@example.com",
                "phone": "9876543210",
                "address": "Test delivery address",
                "coupon": "",
            },
        )

    def test_payment_page_shows_methods_and_inr_total(self):
        response = self.client.get(reverse("payment"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cash on Delivery")
        self.assertContains(response, "UPI")
        self.assertContains(response, "Card")
        self.assertContains(response, "₹251.00")
        self.assertContains(response, "not processed online")
        self.assertNotContains(response, "Razorpay")

    def test_catalog_cart_and_payment_pages_format_prices_as_inr(self):
        shop_response = self.client.get(reverse("shop"), {"q": "Test shirt"})
        product_response = self.client.get(reverse("product", args=[self.product.pk]))
        cart_response = self.client.get(reverse("cart"))
        payment_response = self.client.get(reverse("payment"))

        self.assertEqual(shop_response.status_code, 200)
        shop_html = shop_response.content.decode("utf-8")
        product_html = product_response.content.decode("utf-8")
        self.assertIn('<span class="price-currency">₹</span>', shop_html)
        self.assertIn('<span class="price-amount">125.50</span>', shop_html)
        self.assertIn('<span class="price-symbol">₹</span>', product_html)
        self.assertIn('<span class="price-val">125.50</span>', product_html)
        self.assertIn("₹125.50", cart_response.content.decode("utf-8"))
        self.assertIn("₹251.00", payment_response.content.decode("utf-8"))

    def test_adding_to_cart_from_wishlist_removes_product_from_wishlist(self):
        session = self.client.session
        session["wishlist"] = [self.product.pk]
        session.save()

        wishlist_response = self.client.get(reverse("wishlist"))
        self.assertContains(
            wishlist_response,
            'name="remove_from_wishlist" value="1"',
        )

        response = self.client.post(
            reverse("add_to_cart", args=[self.product.pk]),
            {
                "quantity": "1",
                "size": "M",
                "next": reverse("wishlist"),
                "remove_from_wishlist": "1",
            },
        )

        self.assertRedirects(response, reverse("wishlist"))
        self.assertFalse(self.client.session["wishlist"])
        self.assertTrue(
            CartItem.objects.filter(
                session_key=self.client.session.session_key,
                product=self.product,
                size="M",
            ).exists()
        )

    def test_product_detail_has_add_to_wishlist_control(self):
        response = self.client.get(reverse("product", args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add to Wishlist")
        self.assertContains(response, reverse("toggle_wishlist", args=[self.product.pk]))

    def test_adding_to_cart_elsewhere_keeps_product_on_wishlist(self):
        session = self.client.session
        session["wishlist"] = [self.product.pk]
        session.save()

        self.client.post(
            reverse("add_to_cart", args=[self.product.pk]),
            {"quantity": "1", "size": "M"},
        )

        self.assertEqual(self.client.session["wishlist"], [self.product.pk])

    def test_customer_can_submit_review_and_product_shows_real_rating(self):
        response = self.client.post(
            reverse("submit_review", args=[self.product.pk]),
            {"rating": "4", "body": "Great fit and quality."},
        )

        self.assertRedirects(response, reverse("product", args=[self.product.pk]))
        review = Review.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.body, "Great fit and quality.")

        product_response = self.client.get(reverse("product", args=[self.product.pk]))
        self.assertContains(product_response, "4.0")
        self.assertContains(product_response, "Great fit and quality.")
        self.assertContains(product_response, "1 review")

    def test_customer_can_update_their_existing_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=2,
            body="It was okay.",
        )

        self.client.post(
            reverse("submit_review", args=[self.product.pk]),
            {"rating": "5", "body": "Changed my mind; excellent product."},
        )

        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.body, "Changed my mind; excellent product.")
        self.assertEqual(Review.objects.filter(product=self.product).count(), 1)

    def test_invalid_review_is_not_saved(self):
        response = self.client.post(
            reverse("submit_review", args=[self.product.pk]),
            {"rating": "6", "body": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["review_form"].errors)
        self.assertFalse(Review.objects.filter(product=self.product).exists())

    def test_review_submission_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse("submit_review", args=[self.product.pk]),
            {"rating": "5", "body": "Nice product."},
        )

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(Review.objects.filter(product=self.product).exists())

    def test_valid_payment_preference_creates_order_and_clears_cart(self):
        response = self.client.post(
            reverse("payment"),
            {"payment_method": "upi"},
        )

        self.assertRedirects(response, reverse("cart"))
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.payment_method, "upi")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.total, Decimal("251.00"))
        self.assertEqual(order.items.count(), 1)
        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.quantity, 2)
        self.assertFalse(
            CartItem.objects.filter(session_key=self.client.session.session_key).exists()
        )

    def test_invalid_payment_method_does_not_create_order_or_clear_cart(self):
        response = self.client.post(
            reverse("payment"),
            {"payment_method": "paypal"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        self.assertTrue(
            CartItem.objects.filter(session_key=self.client.session.session_key).exists()
        )
