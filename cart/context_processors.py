from products.models import Product
from .utils import get_cart


def cart_contents(request):
    cart = get_cart(request)
    cart_items = []
    cart_total = 0
    cart_count = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue

        quantity = min(quantity, product.stock_quantity)
        line_total = product.current_price * quantity
        cart_total += line_total
        cart_count += quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    return {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_count": cart_count,
    }
