from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from wishlist.models import WishlistItem


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_slug = request.GET.get("category", "all")
    sort = request.GET.get("sort", "name")

    # Category filtering
    if category_slug != "all":
        products = products.filter(category__slug=category_slug)

    # Sorting
    if sort == "name":
        products = products.order_by("name")
    elif sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    elif sort == "oldest":
        products = products.order_by("created_at")

    wishlisted_product_ids = []

    if request.user.is_authenticated:
        wishlisted_product_ids = list(
            WishlistItem.objects.filter(
                user=request.user
            ).values_list("product_id", flat=True)
        )

    context = {
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": sort,
        "wishlisted_product_ids": wishlisted_product_ids,
    }

    return render(request, "products/shop.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    is_wishlisted = False

    if request.user.is_authenticated:
        is_wishlisted = WishlistItem.objects.filter(
            user=request.user,
            product=product
        ).exists()

    context = {
        "product": product,
        "is_wishlisted": is_wishlisted,
    }

    return render(request, "products/product_detail.html", context)
