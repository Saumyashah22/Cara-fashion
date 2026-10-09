from .models import CartItem


def wishlist_ids(request):
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


def cart_count(request):
    count = 0
    if request.session.session_key:
        count = sum(
            item.quantity
            for item in CartItem.objects.filter(session_key=request.session.session_key)
        )
    return {"cart_count": count}


def wishlist_count(request):
    return {
        "wishlist_count": len(wishlist_ids(request)),
        "wishlist_ids": wishlist_ids(request),
    }
