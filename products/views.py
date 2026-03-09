from django.shortcuts import render, get_object_or_404
from .models import Product, Category


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

    context = {
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": sort,
    }

    return render(request, "products/shop.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    context = {
        "product": product,
    }

    return render(request, "products/product_detail.html", context)
