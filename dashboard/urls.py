from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:product_id>/edit/", views.edit_product, name="edit_product"),
    path("products/<int:product_id>/toggle-active/", views.toggle_product_active, name="toggle_product_active"),
    path("products/<int:product_id>/delete/", views.delete_product, name="delete_product"),
    path("products/<int:product_id>/images/add/", views.add_product_image, name="add_product_image"),
    path("images/<int:image_id>/delete/", views.delete_product_image, name="delete_product_image"),
    path("categories/add/", views.add_category, name="add_category"),
    path("orders/<str:order_number>/", views.order_detail, name="dashboard_order_detail"),
]
