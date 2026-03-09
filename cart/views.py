from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .utils import get_cart, save_cart


def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    cart_total = 0
    updated_cart = {}
    removed_any = False

    for product_id, quantity in cart.items():
        try:
            if request.user.is_authenticated and request.user.is_staff:
                product = Product.objects.get(pk=product_id)
            else:
                product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            removed_any = True
            continue

        # Safety check in case stock changed after item was added
        quantity = min(quantity, product.stock_quantity)

        # Remove item entirely if stock is now zero
        if quantity < 1:
            removed_any = True
            continue

        updated_cart[str(product.id)] = quantity

        line_total = product.current_price * quantity
        cart_total += line_total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    if removed_any:
        save_cart(request, updated_cart)
        messages.warning(
            request,
            "Some unavailable items were removed from your cart."
        )

    return render(request, "cart/cart.html", {
        "cart_items": cart_items,
        "cart_total": cart_total,
    })


def add_to_cart(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        product = get_object_or_404(Product, pk=product_id)
    else:
        product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.method != "POST":
        return redirect("product_detail", slug=product.slug)

    if not product.is_active:
        messages.error(request, "This product is currently unavailable.")
        return redirect("shop")

    if product.stock_quantity < 1:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(request.POST.get("redirect_url", "shop"))

    cart = get_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    product_id_str = str(product.id)
    current_quantity = cart.get(product_id_str, 0)
    new_quantity = current_quantity + quantity

    if new_quantity > product.stock_quantity:
        new_quantity = product.stock_quantity
        messages.warning(
            request,
            f"Only {product.stock_quantity} of {product.name} available in stock."
        )

    cart[product_id_str] = new_quantity
    save_cart(request, cart)

    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("redirect_url", "shop"))


def update_cart(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        product = get_object_or_404(Product, pk=product_id)
    else:
        product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.method != "POST":
        return redirect("cart_detail")

    if not product.is_active:
        messages.error(request, "This product is currently unavailable.")
        return redirect("cart_detail")

    cart = get_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    product_id_str = str(product.id)

    if quantity < 1:
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

    if quantity < 1:
        cart.pop(product_id_str, None)
        save_cart(request, cart)
        messages.info(request, f"{product.name} removed from your cart.")
        return redirect("cart_detail")

    cart[product_id_str] = quantity
    save_cart(request, cart)

    messages.success(request, f"{product.name} quantity updated.")
    return redirect("cart_detail")


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)

    product = Product.objects.filter(pk=product_id).first()

    if product_id_str in cart:
        cart.pop(product_id_str)
        save_cart(request, cart)

        if product:
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.success(request, "Item removed from your cart.")

    return redirect("cart_detail")
