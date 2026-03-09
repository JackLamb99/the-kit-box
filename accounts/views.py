from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomLoginForm


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
