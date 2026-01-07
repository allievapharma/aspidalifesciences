from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken , TokenError
from rest_framework.permissions import IsAuthenticated


from .serializers import (UserRegistrationSerializer , UserLoginSerializer , UserProfileSerializer ,
                           UserChangePasswordSerializer , ForgotPasswordSerializer, ResetPasswordSerializer,
                          RegistrationOTPSerializer)

from .renderers import UserRenderer

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegistrationOTPView(APIView):
    def post(self, request):
        serializer = RegistrationOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=200)


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = get_tokens(user)
        return Response(
            {"msg": "Registration successful", "token": token},
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            token = get_tokens(user)
            return Response(
                {"msg": "Login successful", "token": token},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": {"non_field_errors": ["Invalid login credentials"]}},
            status=status.HTTP_401_UNAUTHORIZED,
        )

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({"profile": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"msg": "Profile updated successfully", "profile": serializer.data},
            status=status.HTTP_200_OK
        )



class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if refresh_token is None:
                return Response(
                    {"errors": {"refresh": ["Refresh token is required"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"msg": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError:
            return Response(
                {"errors": {"refresh": ["Invalid or expired refresh token"]}},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data,
            context={"user": request.user}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"msg": "Password changed successfully."},
            status=status.HTTP_200_OK
        )

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

