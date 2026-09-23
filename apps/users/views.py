from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


def _set_auth_cookie(response, name, token, lifetime):
    response.set_cookie(
        key=name,
        value=token,
        max_age=int(lifetime.total_seconds()),
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="Lax",
        path="/",
    )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)





class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        response = Response(UserSerializer(user).data)
        _set_auth_cookie(
            response,
            "access_token",
            str(refresh.access_token),
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        )
        _set_auth_cookie(
            response,
            "refresh_token",
            str(refresh),
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        )
        return response


class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data={"refresh": request.COOKIES.get("refresh_token")})
        serializer.is_valid(raise_exception=True)

        token_data = serializer.validated_data
        response = Response({"detail": "Tokens refreshed."})
        _set_auth_cookie(
            response,
            "access_token",
            token_data["access"],
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        )
        if "refresh" in token_data:
            _set_auth_cookie(
                response,
                "refresh_token",
                token_data["refresh"],
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            )
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response(
            {"detail": "Logged out successfully."},
            status=200,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
