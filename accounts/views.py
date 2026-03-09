from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from checkout.models import Order
from .forms import CustomUserCreationForm, CustomLoginForm, UserDetailsForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = CustomLoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if next_url:
                return redirect(next_url)
            return redirect("home")
    else:
        form = CustomLoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_url,
        }
    )


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def account_view(request):
    section = request.GET.get("section", "details")
    order_sort = request.GET.get("order_sort", "newest")

    if request.method == "POST":
        form = UserDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?updated=true")
    else:
        form = UserDetailsForm(instance=request.user)

    orders = Order.objects.filter(user=request.user)

    if order_sort == "oldest":
        orders = orders.order_by("created_at")
    else:
        orders = orders.order_by("-created_at")

    context = {
        "account_section": section,
        "form": form,
        "orders": orders,
        "current_order_sort": order_sort,
    }

    return render(request, "accounts/account.html", context)


@login_required
def account_order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("lineitems__product"),
        order_number=order_number,
        user=request.user
    )

    return render(request, "accounts/order_detail.html", {
        "order": order,
    })
