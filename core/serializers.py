from rest_framework import serializers
from .models import (
	Category , SubCategory , Brand , Manufacturer ,
	SaltComposition , Product , ProductImage ,
	Address , Cart , Wishlist , Order , OrderItem ,
)


class ProductImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductImage
		fields = ["id" , "image"]


# class ReviewSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)
#
#     class Meta:
#         model = Review
#         fields = ["id", "user", "rating", "comment", "created_at"]
#         # fields = ["id", "rating", "comment", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
	images = ProductImageSerializer(many=True , read_only=True)
	# reviews = ReviewSerializer(many=True, read_only=True)
	brand = serializers.StringRelatedField(read_only=True)
	manufacturer = serializers.StringRelatedField()
	salt_compositions = serializers.StringRelatedField(many=True)
	subcategory = serializers.StringRelatedField()
	
	discount_percentage = serializers.FloatField(read_only=True)
	
	class Meta:
		model = Product
		fields = "__all__"


class SubCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = SubCategory
		fields = ["id" , "name" , "slug"]


class CategorySerializer(serializers.ModelSerializer):
	subcategories = SubCategorySerializer(many=True , read_only=True)
	
	class Meta:
		model = Category
		fields = ["id" , "name" , "slug" , "subcategories"]


class BrandSerializer(serializers.ModelSerializer):
	class Meta:
		model = Brand
		fields = "__all__"


class ManufacturerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Manufacturer
		fields = "__all__"


class SaltCompositionSerializer(serializers.ModelSerializer):
	class Meta:
		model = SaltComposition
		fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = "__all__"
		read_only_fields = ["user"]


class CartSerializer(serializers.ModelSerializer):
	product_detail = serializers.SerializerMethodField()
	line_total = serializers.SerializerMethodField()
	
	class Meta:
		model = Cart
		fields = "__all__"
		read_only_fields = ["user"]
	
	def get_product_detail(self , obj):
		first_image = None
		image = obj.product.images.first()
		if image:
			first_image = image.image.url
		
		return {
			"id": obj.product.id ,
			"name": obj.product.name ,
			"base_price": obj.product.base_price ,
			"selling_price": obj.product.selling_price ,
			"image": first_image ,
		}
	
	def get_line_total(self , obj):
		return obj.product.selling_price * obj.quantity


class WishlistSerializer(serializers.ModelSerializer):
	product_detail = serializers.SerializerMethodField()
	
	class Meta:
		model = Wishlist
		fields = "__all__"
		read_only_fields = ["user"]
	
	def get_product_detail(self , obj):
		return {
			"id": obj.product.id ,
			"name": obj.product.name ,
			"selling_price": obj.product.selling_price ,
		}


class OrderItemSerializer(serializers.ModelSerializer):
	product_detail = serializers.SerializerMethodField()
	line_total = serializers.SerializerMethodField()
	
	class Meta:
		model = OrderItem
		fields = [
			"id" ,
			"product" ,
			"quantity" ,
			"price" ,
			"line_total" ,
			"product_detail" ,
		]
		read_only_fields = ["price"]
	
	def get_product_detail(self , obj):
		return {
			"id": obj.product.id ,
			"name": obj.product.name ,
			"slug": obj.product.slug ,
			"selling_price": obj.product.selling_price ,
		}
	
	def get_line_total(self , obj):
		return obj.price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True , read_only=True)
	
	class Meta:
		model = Order
		fields = [
			"id" ,
			"user" ,
			"address" ,
			"total_amount" ,
			"order_status" ,
			"payment_status" ,
			"payment_id" ,
			"created_at" ,
			"updated_at" ,
			"items" ,
		]
		read_only_fields = [
			"user" ,
			"total_amount" ,
			"order_status" ,
			"payment_status" ,
			"payment_id" ,
			"created_at" ,
			"updated_at" ,
		]


class CheckoutSerializer(serializers.Serializer):
	address_id = serializers.IntegerField()
	
	def validate_address_id(self , value):
		user = self.context["request"].user
		if not Address.objects.filter(id=value , user=user).exists():
			raise serializers.ValidationError("Invalid address")
		return value