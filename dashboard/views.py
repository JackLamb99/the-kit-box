from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product, Category, ProductImage
from products.forms import ProductForm, CategoryForm, ProductImageForm
from checkout.models import Order


def staff_check(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_check)
def dashboard_home(request):
    section = request.GET.get("section", "products")

    products = Product.objects.select_related("category")
    categories = Category.objects.all()

    category_slug = request.GET.get("category", "all")
    product_sort = request.GET.get("sort", "name")
    order_sort = request.GET.get("order_sort", "newest")

    if category_slug != "all":
        products = products.filter(category__slug=category_slug)

    if product_sort == "name":
        products = products.order_by("name")
    elif product_sort == "price_asc":
        products = products.order_by("price")
    elif product_sort == "price_desc":
        products = products.order_by("-price")
    elif product_sort == "stock_asc":
        products = products.order_by("stock_quantity")
    elif product_sort == "stock_desc":
        products = products.order_by("-stock_quantity")
    elif product_sort == "newest":
        products = products.order_by("-created_at")
    elif product_sort == "oldest":
        products = products.order_by("created_at")
    else:
        products = products.order_by("name")

    orders = Order.objects.select_related("user")

    if order_sort == "oldest":
        orders = orders.order_by("created_at")
    else:
        orders = orders.order_by("-created_at")

    context = {
        "dashboard_section": section,
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "current_sort": product_sort,
        "orders": orders,
        "current_order_sort": order_sort,
    }

    return render(request, "dashboard/dashboard_home.html", context)


@login_required
@user_passes_test(staff_check)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect("dashboard_home")
    else:
        form = ProductForm()

    return render(request, "dashboard/product_form.html", {
        "form": form,
        "page_title": "Add Product",
        "submit_text": "Create Product",
    })


@login_required
@user_passes_test(staff_check)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("edit_product", product_id=product.id)
    else:
        form = ProductForm(instance=product)

    image_form = ProductImageForm()

    return render(request, "dashboard/product_form.html", {
        "form": form,
        "product": product,
        "images": images,
        "image_form": image_form,
        "page_title": f"Edit Product: {product.name}",
        "submit_text": "Save Changes",
    })


@login_required
@user_passes_test(staff_check)
def toggle_product_active(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.is_active = not product.is_active
        product.save()

        if product.is_active:
            messages.success(request, f"{product.name} is now active.")
        else:
            messages.success(request, f"{product.name} has been disabled.")

    return redirect("dashboard_home")


@login_required
@user_passes_test(staff_check)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(request, f"{product_name} was deleted successfully.")

    return redirect("dashboard_home")


@login_required
@user_passes_test(staff_check)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("add_product")
    else:
        form = CategoryForm()

    return render(request, "dashboard/category_form.html", {
        "form": form,
        "page_title": "Add Category",
        "submit_text": "Create Category",
    })


@login_required
@user_passes_test(staff_check)
def add_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.images.count() >= 5:
        messages.error(request, "Maximum of 5 images allowed.")
        return redirect("edit_product", product_id=product.id)

    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save(commit=False)
            image.product = product

            if image.is_primary:
                ProductImage.objects.filter(product=product).update(is_primary=False)

            image.save()
            messages.success(request, "Image uploaded successfully.")

    return redirect("edit_product", product_id=product.id)


@login_required
@user_passes_test(staff_check)
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted.")

    return redirect("edit_product", product_id=product_id)


@login_required
@user_passes_test(staff_check)
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("lineitems__product"),
        order_number=order_number
    )

    return render(request, "dashboard/order_detail.html", {
        "order": order,
    })
