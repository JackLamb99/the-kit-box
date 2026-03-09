from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0
    readonly_fields = ("product", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "full_name",
        "email",
        "display_country",
        "total",
        "created_at",
    )

    list_filter = (
        "country",
        "created_at",
    )

    search_fields = (
        "order_number",
        "full_name",
        "email",
        "phone_number",
        "address_line_1",
        "postcode",
        "stripe_payment_intent_id",
    )

    readonly_fields = (
        "order_number",
        "user",
        "full_name",
        "email",
        "phone_number",
        "address_line_1",
        "address_line_2",
        "city",
        "county",
        "postcode",
        "country",
        "total",
        "stripe_payment_intent_id",
        "created_at",
    )

    fieldsets = (
        ("Order Information", {
            "fields": (
                "order_number",
                "user",
                "total",
                "stripe_payment_intent_id",
                "created_at",
            )
        }),
        ("Customer Details", {
            "fields": (
                "full_name",
                "email",
                "phone_number",
            )
        }),
        ("Delivery Details", {
            "fields": (
                "address_line_1",
                "address_line_2",
                "city",
                "county",
                "postcode",
                "country",
            )
        }),
    )

    ordering = ("-created_at",)
    inlines = [OrderLineItemInline]

    @admin.display(description="Country")
    def display_country(self, obj):
        return obj.get_country_display()
