import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CheckoutForm
from .models import Order, OrderLineItem
from .utils import cart_has_valid_stock, get_cart_data


stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    cart_data = get_cart_data(request)
    cart_items = cart_data["cart_items"]
    total = cart_data["total"]

    stock_ok, problem_product = cart_has_valid_stock(cart_items)
    if not stock_ok:
        messages.error(
            request,
            f"Sorry, there is not enough stock for {problem_product.name}."
        )
        return redirect("cart")

    initial_data = {}

    if request.user.is_authenticated:
        initial_data = {
            "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "email": request.user.email,
            "phone_number": request.user.phone_number,
            "address_line_1": request.user.address_line_1,
            "address_line_2": request.user.address_line_2,
            "city": request.user.town_or_city,
            "county": request.user.county,
            "postcode": request.user.postcode,
            "country": request.user.country,
        }

    form = CheckoutForm(initial=initial_data)

    intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency=settings.STRIPE_CURRENCY,
        metadata={
            "username": request.user.email if request.user.is_authenticated else "guest",
        },
    )

    context = {
        "form": form,
        "cart_items": cart_items,
        "cart_total": total,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": intent.client_secret,
    }
    return render(request, "checkout/checkout.html", context)


@require_POST
def checkout_complete(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    form = CheckoutForm(request.POST)
    payment_intent_id = request.POST.get("payment_intent_id", "")

    if not form.is_valid():
        cart_data = get_cart_data(request)
        total = cart_data["total"]

        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency=settings.STRIPE_CURRENCY,
        )

        context = {
            "form": form,
            "cart_items": cart_data["cart_items"],
            "cart_total": total,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "client_secret": intent.client_secret,
        }
        return render(request, "checkout/checkout.html", context)

    cart_data = get_cart_data(request)
    cart_items = cart_data["cart_items"]
    total = cart_data["total"]

    stock_ok, problem_product = cart_has_valid_stock(cart_items)
    if not stock_ok:
        messages.error(
            request,
            f"Sorry, there is not enough stock for {problem_product.name}."
        )
        return redirect("cart")

    order = form.save(commit=False)

    if request.user.is_authenticated:
        order.user = request.user

    order.total = total
    order.stripe_payment_intent_id = payment_intent_id
    order.save()

    for item in cart_items:
        product = item["product"]
        quantity = item["quantity"]

        OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            line_total=item["line_total"],
        )

        product.stock_quantity -= quantity
        product.save()

    request.session["cart"] = {}

    return redirect("checkout_success", order_number=order.order_number)


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    context = {
        "order": order,
    }
    return render(request, "checkout/checkout_success.html", context)
