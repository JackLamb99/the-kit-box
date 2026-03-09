def get_cart(request):
    """
    Return the cart from the session.
    Creates an empty cart if one does not already exist.
    """
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return cart


def save_cart(request, cart):
    """
    Save the cart back into the session.
    """
    request.session["cart"] = cart
    request.session.modified = True
