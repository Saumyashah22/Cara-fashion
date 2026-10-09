from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError, models, transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import BlogPost, CartItem, ContactMessage, Newsletter, Order, OrderItem, Product, Review


def session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def wishlist_product_ids(request):
    raw_ids = request.session.get("wishlist", [])
    if not isinstance(raw_ids, list):
        raw_ids = [raw_ids]

    parsed = []
    for value in raw_ids:
        try:
            item_id = int(value)
        except (TypeError, ValueError):
            continue
        if item_id not in parsed:
            parsed.append(item_id)

    request.session["wishlist"] = parsed
    return parsed


def cart_items_for(request):
    return CartItem.objects.filter(session_key=session_key(request)).select_related("product")


def home(request):
    return render(
        request,
        "store/home.html",
        {
            "featured": Product.objects.filter(featured=True),
            "new_arrivals": Product.objects.filter(new_arrival=True),
            "categories": Product.objects.values_list("category", flat=True).distinct().order_by("category"),
        },
    )


def shop(request):
    products = Product.objects.all()
    category = request.GET.get("category", "").strip()
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "").strip()

    if category:
        products = products.filter(category__iexact=category)
    if q:
        products = products.filter(
            models.Q(name__icontains=q)
            | models.Q(brand__icontains=q)
            | models.Q(description__icontains=q)
            | models.Q(category__icontains=q)
        )

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-id")
    else:
        products = products.order_by("id")

    categories = Product.objects.values_list("category", flat=True).distinct().order_by("category")
    paginator = Paginator(products, 8)
    page_number = request.GET.get("page") or 1
    page = paginator.get_page(page_number)

    return render(
        request,
        "store/shop.html",
        {
            "page": page,
            "current_category": category,
            "search_query": q,
            "current_sort": sort,
            "categories": categories,
            "total_count": products.count(),
        },
    )


@login_required(login_url="login")
def product_detail(request, pk, review_form=None):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.exclude(pk=pk).filter(category=product.category)[:4]
    if not related:
        related = Product.objects.exclude(pk=pk)[:4]
    reviews = Review.objects.filter(product=product).select_related("user")
    user_review = reviews.filter(user=request.user).first()
    return render(
        request,
        "store/product.html",
        {
            "product": product,
            "related": related,
            "reviews": reviews,
            "review_count": reviews.count(),
            "average_rating": reviews.aggregate(average=Avg("rating"))["average"],
            "review_form": review_form or ReviewForm(instance=user_review),
            "user_review": user_review,
        },
    )


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def submit_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user_review = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=user_review)
    if form.is_valid():
        saved_review = form.save(commit=False)
        saved_review.product = product
        saved_review.user = request.user
        saved_review.save()
        messages.success(request, "Your review has been saved.")
        return redirect("product", pk=product.pk)
    return product_detail(request, pk, review_form=form)


@login_required(login_url="login")
def cart(request):
    items = cart_items_for(request)
    subtotal = sum((item.subtotal for item in items), Decimal("0.00"))

    # Coupon handling
    applied_coupon = request.GET.get("coupon", "").strip()
    if not applied_coupon:
        applied_coupon = request.session.get("applied_coupon", "")

    discount = Decimal("0.00")
    coupon_valid = False
    if applied_coupon.upper() == "CARA10":
        discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
        coupon_valid = True
        request.session["applied_coupon"] = "CARA10"
    elif applied_coupon:
        messages.error(request, f"Coupon code '{applied_coupon}' is invalid.")
        request.session.pop("applied_coupon", None)
        applied_coupon = ""

    total = max(Decimal("0.00"), subtotal - discount)
    return render(
        request,
        "store/cart.html",
        {
            "items": items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "coupon": applied_coupon,
            "coupon_valid": coupon_valid,
        },
    )


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qty = max(1, int(request.POST.get("quantity") or 1))
    size = (request.POST.get("size") or "M").strip()[:8] or "M"
    key = session_key(request)
    item, created = CartItem.objects.get_or_create(
        session_key=key,
        product=product,
        size=size,
        defaults={"quantity": qty},
    )
    if not created:
        item.quantity += qty
        item.save()
    if request.POST.get("remove_from_wishlist") == "1":
        product_ids = wishlist_product_ids(request)
        if pk in product_ids:
            product_ids.remove(pk)
            request.session["wishlist"] = product_ids
            messages.info(request, f"{product.name} removed from your wishlist.")
    messages.success(request, f"{product.brand} added to your cart.")
    return redirect(request.POST.get("next") or "cart")


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def update_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, session_key=session_key(request))
    item.quantity = max(1, int(request.POST.get("quantity") or 1))
    item.save()
    return redirect("cart")


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def remove_from_cart(request, pk):
    CartItem.objects.filter(pk=pk, session_key=session_key(request)).delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def checkout(request):
    name = request.POST.get("customer_name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    coupon = request.POST.get("coupon", "").strip()
    if not all([name, email, phone, address]):
        messages.error(request, "Please fill name, email, phone, and address.")
        return redirect("cart")

    if not cart_items_for(request).exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    if coupon and coupon.upper() != "CARA10":
        messages.error(request, f"Coupon code '{coupon}' is invalid.")
        return redirect("cart")

    request.session["checkout_details"] = {
        "customer_name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "coupon": "CARA10" if coupon.upper() == "CARA10" else "",
    }
    return redirect("payment")


@login_required(login_url="login")
def payment(request):
    items = list(cart_items_for(request))
    details = request.session.get("checkout_details")
    if not items or not isinstance(details, dict):
        messages.info(request, "Enter your delivery details to continue to payment.")
        return redirect("cart")

    subtotal = sum((item.subtotal for item in items), Decimal("0.00"))
    coupon = details.get("coupon", "")
    discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01")) if coupon == "CARA10" else Decimal("0.00")
    total = subtotal - discount

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "")
        allowed_methods = {choice[0] for choice in Order.PAYMENT_METHOD_CHOICES}
        if payment_method not in allowed_methods:
            messages.error(request, "Please select a valid payment method.")
        else:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    customer_name=details["customer_name"],
                    email=details["email"],
                    phone=details["phone"],
                    address=details["address"],
                    coupon=coupon,
                    total=total,
                    payment_method=payment_method,
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        size=item.size,
                        quantity=item.quantity,
                        price=item.product.price,
                    )
                CartItem.objects.filter(session_key=session_key(request)).delete()
            request.session.pop("checkout_details", None)
            request.session.pop("applied_coupon", None)
            messages.success(
                request,
                f"Order #{order.id} placed successfully! Total: ₹{total}. Thank you for shopping with Cara.",
            )
            return redirect("cart")

    return render(
        request,
        "store/payment.html",
        {
            "items": items,
            "details": details,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "payment_methods": Order.PAYMENT_METHOD_CHOICES,
        },
    )


@login_required(login_url="login")
def wishlist(request):
    product_ids = wishlist_product_ids(request)
    products = Product.objects.filter(id__in=product_ids).order_by("id") if product_ids else Product.objects.none()
    return render(request, "store/wishlist.html", {"products": products, "count": len(product_ids)})


@require_POST
@login_required(login_url="login", redirect_field_name=None)
def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_ids = wishlist_product_ids(request)
    if pk in product_ids:
        product_ids.remove(pk)
        messages.info(request, f"{product.name} removed from your wishlist.")
    else:
        product_ids.append(pk)
        messages.success(request, f"{product.name} added to your wishlist.")
    request.session["wishlist"] = product_ids
    return redirect(request.POST.get("next") or "wishlist")


def about(request):
    return render(request, "store/about.html")


def blog(request):
    return render(request, "store/blog.html", {"posts": BlogPost.objects.all()})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        if not all([name, email, subject, message]):
            messages.error(request, "Please fill in every contact field.")
        else:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            messages.success(request, "Thanks — your message was saved.")
            return redirect("contact")
    return render(request, "store/contact.html")


@require_POST
def newsletter(request):
    email = request.POST.get("email", "").strip()
    if not email or "@" not in email:
        messages.error(request, "Enter a valid email address.")
    else:
        try:
            Newsletter.objects.create(email=email)
            messages.success(request, "You are signed up for newsletters.")
        except IntegrityError:
            messages.info(request, "This email is already subscribed.")
    return redirect(request.POST.get("next") or "home")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not all([first_name, username, email, password1, password2]):
            messages.error(request, "Please fill in all required fields.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match. Please try again.")
        elif len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Try another.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, f"Welcome to Cara Fashion, {first_name}! Your account has been created.")
            return redirect("home")
    return render(request, "store/signup.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request, "store/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect("home")
