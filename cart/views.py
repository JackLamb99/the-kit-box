from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .utils import get_cart, save_cart


def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)

        # Safety check in case stock changed after item was added
        quantity = min(quantity, product.stock_quantity)
        line_total = product.current_price * quantity
        cart_total += line_total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    return render(request, "cart/cart.html", {
        "cart_items": cart_items,
        "cart_total": cart_total,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method != "POST":
        return redirect("product_detail", product_id=product.id)

    cart = get_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    # Prevent quantity below 1
    if quantity < 1:
        quantity = 1

    product_id_str = str(product.id)
    current_quantity = cart.get(product_id_str, 0)
    new_quantity = current_quantity + quantity

    # Prevent exceeding stock
    if new_quantity > product.stock_quantity:
        new_quantity = product.stock_quantity
        messages.warning(
            request,
            f"Only {product.stock_quantity} of {product.name} available in stock."
        )

    if product.stock_quantity < 1:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.POST.get("redirect_url", "shop"))

    cart[product_id_str] = new_quantity
    save_cart(request, cart)

    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("redirect_url", "shop"))


def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method != "POST":
        return redirect("cart_detail")

    cart = get_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    product_id_str = str(product.id)

    if quantity < 1:
        # If quantity is invalid or below 1, remove item
        cart.pop(product_id_str, None)
        save_cart(request, cart)
        messages.info(request, f"{product.name} removed from your cart.")
        return redirect("cart_detail")

    if quantity > product.stock_quantity:
        quantity = product.stock_quantity
        messages.warning(
            request,
            f"Only {product.stock_quantity} of {product.name} available in stock."
        )

    cart[product_id_str] = quantity
    save_cart(request, cart)

    messages.success(request, f"{product.name} quantity updated.")
    return redirect("cart_detail")


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)

    product_id_str = str(product.id)

    if product_id_str in cart:
        cart.pop(product_id_str)
        save_cart(request, cart)
        messages.success(request, f"{product.name} removed from your cart.")

    return redirect("cart_detail")
