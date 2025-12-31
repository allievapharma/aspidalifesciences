from django.urls import path
from .views import (RegistrationOTPView , UserRegistrationView , UserLoginView , UserProfileView , UserLogoutView ,
                    UserChangePasswordView , ForgotPasswordView , ResetPasswordView)
from rest_framework_simplejwt.views import (
	TokenRefreshView ,
	TokenVerifyView
)

urlpatterns = [
	path('register/request-otp/' , RegistrationOTPView.as_view() , name='register') ,
	path('register/' , UserRegistrationView.as_view() , name='register') ,
	path('login/' , UserLoginView.as_view() , name='login') ,
	path('profile/' , UserProfileView.as_view() , name='profile') ,
	path('logout/' , UserLogoutView.as_view() , name='logout') ,
	path('change-password/' , UserChangePasswordView.as_view() , name='changepassword') ,
	path('password/forgot/' , ForgotPasswordView.as_view() , name="forgot-password") ,
	path('password/reset/' , ResetPasswordView.as_view() , name="reset-password") ,
	
	#   Token management
	path('token/refresh/' , TokenRefreshView.as_view() , name='token_refresh') ,  # Generate new access token
	path('token/verify/' , TokenVerifyView.as_view() , name='token_verify') ,  # Verify token validity

]