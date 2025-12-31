from rest_framework import serializers
from django.utils.encoding import smart_str , force_bytes , DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from sendgrid.helpers.mail import Mail , Content

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import User , RegistrationOTP , PasswordResetOTP
from .utils import generate_otp , send_email , send_sms

User = get_user_model()


class RegistrationOTPSerializer(serializers.Serializer):
	login_input = serializers.CharField()
	
	def validate(self , attrs):
		login = attrs["login_input"].strip()
		
		if "@" in login:
			if User.objects.filter(email=login).exists():
				raise serializers.ValidationError("Email already registered.")
			attrs["email"] = login
			attrs["phone_number"] = None
			attrs["method"] = "email"
		else:
			if User.objects.filter(phone_number=login).exists():
				raise serializers.ValidationError("Phone already registered.")
			attrs["phone_number"] = login
			attrs["email"] = None
			attrs["method"] = "phone"
		
		return attrs
	
	def save(self):
		otp = generate_otp()
		
		RegistrationOTP.objects.create(
			email=self.validated_data["email"] ,
			phone_number=self.validated_data["phone_number"] ,
			otp=otp ,
			expires_at=timezone.now() + timedelta(minutes=10)
		)
		
		if self.validated_data["method"] == "email":
			send_email(
				"Your Registration OTP" ,
				f"Your OTP is {otp}. Valid for 10 minutes." ,
				self.validated_data["email"]
			)
		else:
			send_sms(
				self.validated_data["phone_number"] ,
				f"Your OTP is {otp}. Valid for 10 minutes."
			)
		
		return {"message": "OTP sent successfully."}


class UserRegistrationSerializer(serializers.ModelSerializer):
	password2 = serializers.CharField(write_only=True)
	login_input = serializers.CharField(write_only=True)
	otp = serializers.CharField(write_only=True)
	
	class Meta:
		model = User
		fields = [
			"user_id" , "login_input" , "otp" , "first_name" , "last_name" , "email" ,
			"phone_number" , "address" , "pincode" , "state" , "country" , "profile_photo" ,
			"date_of_birth" , "password" , "password2"
		]
		read_only_fields = ["user_id"]
		extra_kwargs = {"password": {"write_only": True}}
	
	def validate(self , attrs):
		
		if attrs["password"] != attrs["password2"]:
			raise serializers.ValidationError({"password": "Passwords do not match"})
		
		login = attrs["login_input"].strip()
		otp = attrs["otp"].strip()
		
		# Assign email OR phone automatically
		if "@" in login:
			otp_obj = RegistrationOTP.objects.filter(
				email=login , otp=otp
			).order_by("-created_at").first()
			
			attrs["email"] = login
			attrs["phone_number"] = None
			attrs["method"] = "email"
		
		else:
			otp_obj = RegistrationOTP.objects.filter(
				phone_number=login , otp=otp
			).order_by("-created_at").first()
			
			attrs["phone_number"] = login
			attrs["email"] = None
			attrs["method"] = "phone"
		# print("otp", otp_obj)
		
		if not otp_obj:
			raise serializers.ValidationError("Invalid OTP.")
		
		if otp_obj.is_expired():
			raise serializers.ValidationError("OTP expired. Request a new one.")
		
		return attrs
	
	def create(self , validated_data):
		validated_data.pop("password2")
		validated_data.pop("login_input")
		validated_data.pop("otp")
		method = validated_data.pop("method")
		
		password = validated_data.pop("password")
		
		email = validated_data.get("email")
		phone = validated_data.get("phone_number")
		
		# Auto-generate username
		if email:
			base_username = email.split("@")[0]
		else:
			base_username = phone
		
		username = base_username.lower()
		
		# Ensure uniqueness
		
		original = username
		counter = 1
		while User.objects.filter(username=username).exists():
			username = f"{original}{counter}"
			counter += 1
		
		user = User.objects.create_user(
			username=username ,
			password=password ,
			**validated_data
		)
		
		# Cleanup OTP
		RegistrationOTP.objects.filter(
			email=email if method == "email" else None ,
			phone_number=phone if method == "phone" else None ,
		).delete()
		
		return user


class UserLoginSerializer(serializers.Serializer):
	username = serializers.CharField()  # Can be username/email/phone
	password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = [
			"user_id" , "username" , "first_name" , "last_name" , "email" , "phone_number" ,
			"address" , "pincode" , "state" , "country" , "profile_photo" ,
			"date_of_birth" , "created_at" , "updated_at"
		]
		read_only_fields = ["user_id" , "username" , "email" , "phone_number" , "created_at" , "updated_at"]


class UserChangePasswordSerializer(serializers.Serializer):
	old_password = serializers.CharField(
		write_only=True ,
		style={'input_type': 'password'}
	)
	new_password = serializers.CharField(
		write_only=True ,
		style={'input_type': 'password'}
	)
	confirm_password = serializers.CharField(
		write_only=True ,
		style={'input_type': 'password'}
	)
	
	def validate_old_password(self , value):
		user = self.context.get("user")
		if not user.check_password(value):
			raise serializers.ValidationError("Old password is incorrect.")
		return value
	
	def validate(self , attrs):
		new_password = attrs.get("new_password")
		confirm_password = attrs.get("confirm_password")
		
		if new_password != confirm_password:
			raise serializers.ValidationError({
				"confirm_password": "New password and confirm password do not match."
			})
		
		validate_password(new_password)
		
		return attrs
	
	def save(self , **kwargs):
		user = self.context.get("user")
		user.set_password(self.validated_data["new_password"])
		user.save()
		return user


class ForgotPasswordSerializer(serializers.Serializer):
	identifier = serializers.CharField()  # email OR phone number
	
	def validate(self , attrs):
		identifier = attrs["identifier"].strip()
		
		# Determine email or phone
		if "@" in identifier:
			# Email login
			user = User.objects.filter(email__iexact=identifier).first()
			if not user:
				raise serializers.ValidationError("No user found with this email.")
			attrs["user"] = user
			attrs["method"] = "email"
		
		elif identifier.isdigit():
			# Phone login
			user = User.objects.filter(phone_number=identifier).first()
			if not user:
				raise serializers.ValidationError("No user found with this phone number.")
			attrs["user"] = user
			attrs["method"] = "phone"
		
		else:
			raise serializers.ValidationError("Identifier must be email or phone number.")
		
		return attrs
	
	def save(self):
		user = self.validated_data["user"]
		method = self.validated_data["method"]
		
		otp = generate_otp()
		
		# Store OTP
		PasswordResetOTP.objects.create(
			user=user ,
			otp=otp ,
			expires_at=timezone.now() + timedelta(minutes=10)
		)
		
		# Send OTP
		if method == "email":
			send_email(
				"Your Password Reset OTP" ,
				f"Your OTP is {otp}. It is valid for 10 minutes." ,
				user.email
			)
		
		else:  # method == "phone"
			send_sms(
				user.phone_number ,
				f"Your OTP is {otp}. Valid for 10 minutes."
			)
		
		return {"message": f"OTP sent on your {method}."}


class ResetPasswordSerializer(serializers.Serializer):
	identifier = serializers.CharField()
	otp = serializers.CharField(max_length=6)
	new_password = serializers.CharField(write_only=True)
	confirm_password = serializers.CharField(write_only=True)
	
	def validate(self , attrs):
		identifier = attrs.get("identifier")
		otp = attrs.get("otp")
		password = attrs.get("new_password")
		confirm = attrs.get("confirm_password")
		
		if password != confirm:
			raise serializers.ValidationError("Password & Confirm Password do not match.")
		
		validate_password(password)
		
		# Find user
		if "@" in identifier:
			user = User.objects.filter(email=identifier).first()
		else:
			user = User.objects.filter(phone_number=identifier).first()
		
		if not user:
			raise serializers.ValidationError("Invalid user identifier.")
		
		# Find OTP
		otp_obj = PasswordResetOTP.objects.filter(user=user , otp=otp).order_by("-created_at").first()
		
		if not otp_obj:
			raise serializers.ValidationError("Invalid OTP.")
		
		if otp_obj.is_expired():
			raise serializers.ValidationError("OTP expired. Request a new one.")
		
		attrs["user"] = user
		return attrs
	
	def save(self):
		user = self.validated_data["user"]
		new_password = self.validated_data["new_password"]
		
		user.set_password(new_password)
		user.save()
		
		# Delete all OTPs for security
		PasswordResetOTP.objects.filter(user=user).delete()
		
		return {"message": "Password reset successful."}
