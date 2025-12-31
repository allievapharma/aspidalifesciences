from django.contrib import admin
from .models import (
    Category, SubCategory, Brand, Manufacturer,
    SaltComposition, Product, ProductImage, Address, Cart, Wishlist, #Review
)

# Register your models here.

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("category",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email")
    search_fields = ("name",)


@admin.register(SaltComposition)
class SaltCompositionAdmin(admin.ModelAdmin):
    list_display = ("name", "strength")
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "subcategory", "brand", "base_price", "selling_price", "stock", "available")
    list_filter = ("subcategory", "brand", "available", "bestseller", "prescription_required")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ("product", "user", "rating", "created_at")
#     list_filter = ("rating", "created_at")
#     search_fields = ("product__name", "user__username")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "city",
        "state",
        "pincode",
        "phone",
    )
    list_filter = ("city", "state", "country")
    search_fields = ("user__username", "user__email", "name", "city", "pincode")
    ordering = ("-id",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "added_at",
        "total_price",
    )
    list_filter = ("added_at",)
    search_fields = ("user__username", "product__name")
    ordering = ("-added_at",)

    # Show total price column
    def total_price(self, obj):
        return obj.product.selling_price * obj.quantity
    total_price.short_description = "Total"



@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "added_at",
    )
    list_filter = ("added_at",)
    search_fields = ("user__username", "product__name")
    ordering = ("-added_at",)

