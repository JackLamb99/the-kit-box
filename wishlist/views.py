from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .models import WishlistItem


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    wishlist_item = WishlistItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        WishlistItem.objects.create(
            user=request.user,
            product=product
        )

    return redirect(request.META.get("HTTP_REFERER", "shop"))


@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(
        user=request.user,
        product__is_active=True
    ).select_related("product")

    return render(request, "wishlist/wishlist.html", {
        "wishlist_items": wishlist_items,
    })
