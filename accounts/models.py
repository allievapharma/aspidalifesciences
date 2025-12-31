from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin
from django.utils import timezone
import uuid
from django.conf import settings
from datetime import timedelta


class UserManager(BaseUserManager):
	
	def create_user(self , email=None , phone_number=None , password=None , **extra_fields):
		
		extra_fields.pop("username" , None)
		
		if not email and not phone_number:
			raise ValueError("Either email or phone_number is required.")
		
		if email:
			email = self.normalize_email(email)
			base_username = email.split("@")[0]
		else:
			base_username = phone_number
		
		username = base_username.strip().lower()
		
		counter = 1
		while self.model.objects.filter(username=username).exists():
			username = f"{base_username}{counter}"
			counter += 1
		
		user = self.model(
			username=username ,
			email=email ,
			phone_number=phone_number ,
			**extra_fields
		)
		
		if not password:
			raise ValueError("Password is required.")
		
		user.set_password(password)
		user.save(using=self._db)
		return user
	
	def create_superuser(self , email , phone_number , password , **extra_fields):
		extra_fields.setdefault("is_staff" , True)
		extra_fields.setdefault("is_superuser" , True)
		extra_fields.setdefault("is_active" , True)
		
		return self.create_user(email , phone_number , password , **extra_fields)


class User(AbstractBaseUser , PermissionsMixin):
	user_id = models.CharField(primary_key=True , max_length=50 , editable=False , unique=True)
	
	username = models.CharField(max_length=50 , unique=True , )
	email = models.EmailField(unique=True , null=True , blank=True)
	phone_number = models.CharField(max_length=15 , unique=True , null=True , blank=True)
	
	first_name = models.CharField(max_length=50 , blank=True , null=True)
	last_name = models.CharField(max_length=50 , blank=True , null=True)
	address = models.TextField(blank=True , null=True)
	pincode = models.CharField(max_length=10 , blank=True , null=True)
	state = models.CharField(max_length=50 , blank=True , null=True)
	country = models.CharField(max_length=50 , blank=True , null=True)
	profile_photo = models.ImageField(upload_to="profiles/" , blank=True , null=True)
	date_of_birth = models.DateField(blank=True , null=True)
	
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	date_joined = models.DateTimeField(default=timezone.now)
	
	USERNAME_FIELD = "username"
	REQUIRED_FIELDS = ["email" , "phone_number"]
	
	objects = UserManager()
	
	class Meta:
		db_table = "users"
	
	def save(self , *args , **kwargs):
		if not self.user_id:
			base = (self.username[:4]).lower()
			rand = str(uuid.uuid4().int)[:6]
			new_id = f"{base}{rand}"
			
			while User.objects.filter(user_id=new_id).exists():
				rand = str(uuid.uuid4().int)[:6]
				new_id = f"{base}{rand}"
			
			self.user_id = new_id
		
		super().save(*args , **kwargs)
	
	def __str__(self):
		return self.username


class RegistrationOTP(models.Model):
	email = models.EmailField(null=True , blank=True)
	phone_number = models.CharField(max_length=15 , null=True , blank=True)
	otp = models.CharField(max_length=6)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()
	
	def is_expired(self):
		return timezone.now() > self.expires_at
	
	class Meta:
		db_table = "RegistrationOTP"


class PasswordResetOTP(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.CASCADE , related_name="password_reset_otps")
	otp = models.CharField(max_length=6)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()
	
	def is_expired(self):
		return timezone.now() > self.expires_at
	
	def __str__(self):
		return f"{self.user.email or self.user.phone} - {self.otp}"
	
	class Meta:
		db_table = "PasswordResetOTP"