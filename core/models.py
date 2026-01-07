from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.conf import settings
from ckeditor.fields import RichTextField


# Create your models here.

class Category(models.Model):
	name = models.CharField(max_length=150 , unique=True)
	slug = models.SlugField(unique=True , blank=True)
	
	def save(self , *args , **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args , **kwargs)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = 'category'


class SubCategory(models.Model):
	category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name="subcategories")
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True , blank=True)
	
	def save(self , *args , **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)
			# Make slug unique within same category
			slug = base_slug
			counter = 1
			while SubCategory.objects.filter(category=self.category , slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args , **kwargs)
	
	def __str__(self):
		return f"{self.category.name} → {self.name}"
	
	class Meta:
		db_table = 'sub_category'


class Brand(models.Model):
	name = models.CharField(max_length=150 , unique=True)
	description = RichTextField(blank=True , null=True)
	logo = models.ImageField(upload_to="brands/" , blank=True , null=True)
	slug = models.SlugField(unique=True , blank=True)
	
	def save(self , *args , **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args , **kwargs)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = 'brand'


class Manufacturer(models.Model):
	name = models.CharField(max_length=200)
	address = RichTextField(blank=True , null=True)
	contact_email = models.EmailField(blank=True , null=True)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = 'manufacturer'


class SaltComposition(models.Model):
	name = models.CharField(max_length=200)
	strength = models.CharField(max_length=100 , blank=True , null=True)  # e.g. "500mg"
	description = RichTextField(blank=True , null=True)
	
	def __str__(self):
		return f"{self.name} ({self.strength})"
	
	class Meta:
		db_table = 'salt_composition'


class Product(models.Model):
	# Relations
	subcategory = models.ForeignKey(SubCategory , on_delete=models.SET_NULL , null=True , related_name="products")
	brand = models.ForeignKey(Brand , on_delete=models.SET_NULL , null=True , related_name="products")
	manufacturer = models.ForeignKey(Manufacturer , on_delete=models.SET_NULL , null=True , related_name="products")
	salt_compositions = models.ManyToManyField(SaltComposition , blank=True , related_name="products")
	
	# Basic info
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True , blank=True)
	
	# Pricing
	base_price = models.DecimalField(max_digits=10 , decimal_places=2 , blank=True , null=True)
	selling_price = models.DecimalField(max_digits=10 , decimal_places=2 , blank=True , null=True)
	
	# Medicine details
	description = RichTextField(blank=True , null=True)
	uses = RichTextField(blank=True , null=True)
	benefits = RichTextField(blank=True , null=True)
	side_effects = RichTextField(blank=True , null=True)
	dosage = RichTextField(blank=True , null=True)
	storage = RichTextField(blank=True , null=True)
	strength = models.CharField(max_length=100 , blank=True , null=True)  # e.g. "500mg"
	packing = models.CharField(max_length=100 , default="")
	form = models.CharField(max_length=100 , blank=True , null=True)  # e.g. "Tablet", "Syrup", "Injection"
	country = models.CharField(max_length=100 , blank=True , null=True)
	
	# Flags
	bestseller = models.BooleanField(default=False)
	prescription_required = models.BooleanField(default=False)
	
	# Inventory
	stock = models.PositiveIntegerField(default=0)
	available = models.BooleanField(default=True)
	created_at = models.DateField(auto_now_add=True , blank=True , null=True)
	updated_at = models.DateField(auto_now=True , blank=True , null=True)
	
	def save(self , *args , **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)
			slug = base_slug
			counter = 1
			while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args , **kwargs)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = 'product'


class ProductImage(models.Model):
	product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="images")
	image = models.ImageField(upload_to="products/" , blank=True , null=True)
	
	def __str__(self):
		return f"Image for {self.product.name}"
	
	class Meta:
		db_table = 'product_image'


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name="addresses")
	name = models.CharField(max_length=100)  # e.g., "Home", "Work"
	line1 = models.CharField(max_length=255)
	line2 = models.CharField(max_length=255 , blank=True , null=True)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	pincode = models.CharField(max_length=20)
	country = models.CharField(max_length=100 , default="India")
	phone = models.CharField(max_length=15)
	
	def __str__(self):
		return f"{self.name} ({self.city})"
	
	class Meta:
		db_table = 'address'


class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name="cart")
	product = models.ForeignKey(Product , on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	added_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"{self.user.username} → {self.product.name} x {self.quantity}"
	
	class Meta:
		db_table = 'cart'


class Wishlist(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name="wishlist")
	product = models.ForeignKey(Product , on_delete=models.CASCADE)
	added_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"{self.user.username} -> {self.product.name}"
	
	class Meta:
		db_table = 'wishlist'


class Order(models.Model):
	ORDER_STATUS_CHOICES = [
		("pending" , "Pending") ,
		("confirmed" , "Confirmed") ,
		('packed' , 'Packed') ,
		("shipped" , "Shipped") ,
		("delivered" , "Delivered") ,
		("cancelled" , "Cancelled") ,
		('refunded' , 'Refunded') ,
	]
	
	PAYMENT_STATUS_CHOICES = [
		("pending" , "Pending") ,
		("paid" , "Paid") ,
		("failed" , "Failed") ,
		("refunded" , "Refunded") ,
	]
	
	user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name="orders")
	address = models.ForeignKey(Address , on_delete=models.SET_NULL , null=True , blank=True)
	total_amount = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
	order_status = models.CharField(max_length=20 , choices=ORDER_STATUS_CHOICES , default="pending")
	payment_status = models.CharField(max_length=20 , choices=PAYMENT_STATUS_CHOICES , default="pending")
	payment_id = models.CharField(max_length=200 , blank=True , null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def calculate_total(self):
		total = sum(item.price * item.quantity for item in self.items.all())
		self.total_amount = total
		self.save(update_fields=["total_amount"])
	
	def __str__(self):
		return f"Order #{self.id} | {self.user.username}"
	
	class Meta:
		db_table = 'order'
		ordering = ["-created_at"]


class OrderItem(models.Model):
	order = models.ForeignKey(Order , on_delete=models.CASCADE , related_name="items")
	product = models.ForeignKey(Product , on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField()
	price = models.DecimalField(max_digits=10 , decimal_places=2)
	
	def line_total(self):
		return self.price * self.quantity
	
	def __str__(self):
		return f"{self.product} x {self.quantity}"
	
	class Meta:
		db_table = 'orderItem'
		unique_together = ("order" , "product")

# class Payment(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
#     method = models.CharField(max_length=50, choices=[("cod", "Cash on Delivery"), ("online", "Online")])
#     transaction_id = models.CharField(max_length=255, blank=True, null=True)
#     paid = models.BooleanField(default=False)
#     paid_at = models.DateTimeField(blank=True, null=True)
#
#     def __str__(self):
#         return f"Payment for Order #{self.order.id}"
# 	class Meta:
# 		db_table = ''
#
#
# class Review(models.Model):
# 	product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="reviews")
# 	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
# 	rating = models.IntegerField(default=5)  # 1-5 scale
# 	comment = models.TextField(blank=True , null=True)
# 	created_at = models.DateTimeField(auto_now_add=True , blank=True , null=True)
#
# 	def __str__(self):
# 		return f"Review({self.rating}) for {self.product.name}"
#
# 	class Meta:
# 		db_table = 'review'
#
#  MARKETING FEATURES
# class Offer(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="offers", blank=True, null=True)
#     percentage = models.PositiveIntegerField(help_text="Discount in %")
#     active = models.BooleanField(default=True)
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#
#     def __str__(self):
#         return f"{self.percentage}% OFF on {self.product.name if self.product else 'All'}"

# 	class Meta:
# 		db_table = ''
#
#
# class Coupon(models.Model):
#     code = models.CharField(max_length=50, unique=True)
#     discount_percent = models.PositiveIntegerField()
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.code

# 	class Meta:
# 		db_table = ''
#
#
# class Banner(models.Model):
#     title = models.CharField(max_length=200)
#     image = models.ImageField(upload_to="banners/")
#     link = models.URLField(blank=True, null=True)
#     active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title

# 	class Meta:
# 		db_table = ''
#
#
# class DeliverySlot(models.Model):
#     slot = models.CharField(max_length=100)
#     active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.slot

# 	class Meta:
# 		db_table = ''