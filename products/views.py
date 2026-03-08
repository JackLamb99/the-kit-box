from django.shortcuts import render
from .models import Product, Category


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_slug = request.GET.get("category")
    sort = request.GET.get("sort")

    # Category filtering
    if category_slug and category_slug != "all":
        products = products.filter(category__slug=category_slug)

    # Sorting
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    elif sort == "newest":
        products = products.order_by("-created_at")
    elif sort == "oldest":
        products = products.order_by("created_at")

    context = {
        "products": products,
        "categories": categories,
    }

    return render(request, "products/shop.html", context)
