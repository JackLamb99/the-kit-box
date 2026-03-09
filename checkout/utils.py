from decimal import Decimal
from django.shortcuts import get_object_or_404
from products.models import Product


def get_cart_data(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = Decimal("0.00")

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        line_total = product.current_price * quantity
        total += line_total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    return {
        "cart_items": cart_items,
        "total": total,
    }


def cart_has_valid_stock(cart_items):
    for item in cart_items:
        if item["quantity"] > item["product"].stock_quantity:
            return False, item["product"]
    return True, None
