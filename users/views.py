from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, ChangePasswordSerializer, EmployeesListSerializer, EmployeeUpdateSerializer

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserSerializer,
        responses={
            201: openapi.Response('User created successfully', UserSerializer),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Maydonlar to'ldirilmadi yoki bunday username bilan foydalanuvchi mavjud!"
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Autentifikatsiya maʼlumotlari taqdim etilmagan."},
                        {
                            "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                            "code": "token_not_valid",
                            "messages": [
                                {
                                    "token_class": "AccessToken",
                                    "token_type": "access",
                                    "message": "Token yaroqsiz yoki muddati tugagan"
                                }
                            ]
                        }
                    ],
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "detail": "Sizda bu amalni bajarish uchun ruxsat yo‘q"
                    }
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
                    }
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            username = request.data.get('username')
            password = request.data.get('password')
            if username is None:
                return Response({"error": "Foydalanuvchi nomini kiriting!"}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=username).exists():
                return Response({"error": "Bu username bilan foydalanuvchi mavjud!"}, status=status.HTTP_400_BAD_REQUEST)
            if password is None:
                return Response({"error": "Parolni kiriting!"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

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
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description="username"),
                    'fullname': openapi.Schema(type=openapi.TYPE_STRING, description="fullname"),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, description="phone"),
                    'is_admin': openapi.Schema(type=openapi.TYPE_STRING, description="is_staff"),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                }
            )),
            400: openapi.Response(
                description="Invalid credentials",
                examples={
                    "application/json": {
                        "error": "Login yoki parol xato!"
                    }
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
                    }
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'username': user.username,
                'fullname': user.fullname,
                'phone': user.phone,
                'is_admin': user.is_staff,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({"error": "Login yoki parol xato!"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Admin Login endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['username', 'password'],
        ),
        responses={
            200: openapi.Response('Admin Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description="username"),
                    'fullname': openapi.Schema(type=openapi.TYPE_STRING, description="fullname"),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, description="phone"),
                    'is_admin': openapi.Schema(type=openapi.TYPE_STRING, description="is_staff"),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                }
            )),
            400: openapi.Response(
                description="Invalid credentials",
                examples={
                    "application/json": {
                        "error": "Login yoki parol xato!"
                    }
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
                    }
                }
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_staff:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'username': user.username,
                    'fullname': user.fullname,
                    'phone': user.phone,
                    'is_admin': user.is_staff,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            else:
                return Response({"error": "Bu foydalanuvchi admin emas!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Login yoki parol xato!"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
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
            205: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "detail": "Muvaffaqiyatli chiqildi."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid token or other error",
                examples={
                    "application/json": {
                        "error": "Refresh token taqdim etilmagan yoki refresh token xato!"
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Autentifikatsiya maʼlumotlari taqdim etilmagan."},
                        {
                            "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                            "code": "token_not_valid",
                            "messages": [
                                {
                                    "token_class": "AccessToken",
                                    "token_type": "access",
                                    "message": "Token yaroqsiz yoki muddati tugagan"
                                }
                            ]
                        }
                    ],
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
                    }
                }
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token taqdim etilmagan."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Muvaffaqiyatli chiqildi."}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response({"error": "Refresh token xato!"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, TokenError):
            return Response({
                "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                "code": "token_not_valid",
                "messages": [
                    {
                        "token_class": "AccessToken",
                        "token_type": "access",
                        "message": "Token yaroqsiz yoki muddati tugagan"
                    }
                ]
            }, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password updated successfully",
                examples={
                    "application/json": {
                        "detail": "Parolingiz muvaffaqiyatli o'zgartirildi."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": [
                        {"old_password": "Eski parolingiz xato!"},
                        {"new_password": "Yangi parol eski parol bilan bir xil!"},
                        {"old_password": "Eski parol kiritilmagan!"},
                        {"new_password": "Yangi parol kiritilmagan!"}
                    ]
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Autentifikatsiya maʼlumotlari taqdim etilmagan."},
                        {
                            "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                            "code": "token_not_valid",
                            "messages": [
                                {
                                    "token_class": "AccessToken",
                                    "token_type": "access",
                                    "message": "Token yaroqsiz yoki muddati tugagan"
                                }
                            ]
                        }
                    ],
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
                    }
                }
            ),
        }
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.data.get("new_password")
            old_password = serializer.data.get("old_password")
            # Check old password
            if not user.check_password(old_password):
                return Response({"old_password": "Eski parolingiz xato!"}, status=status.HTTP_400_BAD_REQUEST)

            # Check new password
            if old_password == new_password:
                return Response({"new_password": "Yangi parol eski parol bilan bir xil!"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Parolingiz muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)

        else:
            if serializer.errors.get("old_password"):
                return Response({"old_password": "Eski parol kiritilmagan!"}, status=status.HTTP_400_BAD_REQUEST)
            elif serializer.errors.get("new_password"):
                return Response({"new_password": "Yangi parol kiritilmagan!"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
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
                        "detail": "Parol muvaffaqiyatli o'zgartirildi."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input or user not found",
                examples={
                    "application/json": {
                        "error": "Foydalanuvchi topilmadi!"
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Autentifikatsiya maʼlumotlari taqdim etilmagan."},
                        {
                            "detail": "Berilgan token hech qanday token turi uchun yaroqsiz!",
                            "code": "token_not_valid",
                            "messages": [
                                {
                                    "token_class": "AccessToken",
                                    "token_type": "access",
                                    "message": "Token yaroqsiz yoki muddati tugagan"
                                }
                            ]
                        }
                    ],
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "detail": "Sizda bu amalni bajarish uchun ruxsat yo‘q"
                    }
                }
            ),
            405: openapi.Response(
                description="Method Not Allowed",
                examples={
                    "application/json": {
                        "detail": "Bunday amal mavjud emas."
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
            return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Foydalanuvchi topilmadi!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = EmployeesListSerializer
    permission_classes = [IsAdminUser]


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeUpdateAPIView(APIView):
    serializer_class = EmployeeUpdateSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Update an employee's details",
        request_body=EmployeeUpdateSerializer,
        responses={
            200: EmployeeUpdateSerializer,
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Not Found')
        }
    )
    def patch(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Foydalanuvchi topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
