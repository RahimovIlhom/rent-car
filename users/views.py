from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChangePasswordSerializer

User = get_user_model()


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Login endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['username', 'password'],
        ),
        responses={
            200: openapi.Response('Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                }
            )),
            400: 'Invalid credentials'
        }
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            },
            required=['refresh'],
        ),
        responses={
            205: 'Logout successful',
            400: 'Invalid token or other error'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Reset password endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
            required=['user_id', 'new_password'],
        ),
        responses={
            200: openapi.Response(
                description="Password reset successfully",
                examples={
                    "application/json": {
                        "detail": "Password reset successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input or user not found",
                examples={
                    "application/json": {
                        "detail": "User not found."
                    }
                }
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            new_password = request.data.get('new_password')
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
