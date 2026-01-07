from django.urls import path, re_path
from .views import ReactAppView

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SubCategoryViewSet, BrandViewSet, ManufacturerViewSet,
    SaltCompositionViewSet, ProductViewSet, #ReviewViewSet
    AddressViewSet, CartViewSet, WishlistViewSet,
    OrderViewSet, OrderItemViewSet, CheckoutAPIView
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("subcategories", SubCategoryViewSet)
router.register("brands", BrandViewSet)
router.register("manufacturers", ManufacturerViewSet)
router.register("salts", SaltCompositionViewSet)
router.register("products", ProductViewSet)

router.register("addresses", AddressViewSet, basename="addresses")
router.register("cart", CartViewSet, basename="cart")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("orders", OrderViewSet, basename="orders")
router.register("order-items", OrderItemViewSet, basename="order-items")

# router.register("reviews", ReviewViewSet)

urlpatterns = [
	# path("", ReactAppView.as_view(), name="react"),
    path("", include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
]
