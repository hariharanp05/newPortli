import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from mongoengine.errors import DoesNotExist
from .models import User
from .serializers import RegisterSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.contrib.auth.hashers import check_password
# views.py
from rest_framework.permissions import IsAuthenticated

import jwt
from datetime import datetime, timedelta


def generate_jwt(user):
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=1),  # token expires in 1 hour
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


@api_view(['POST'])
def register(request):
    
    
    # Check if a user with this email already exists
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
        if user.is_verified:
            return Response({"error": "User with this email is already registered and verified."}, status=400)
        else:
            # Resend OTP
            user.otp = str(random.randint(100000, 999999))
            user.save()

            send_mail(
                subject="Portli - Your OTP Code (Resent)",
                message=f"Your OTP is {user.otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=not settings.DEBUG
            )

            return Response({"message": "User already exists but is not verified. New OTP sent to email."}, status=200)
    except User.DoesNotExist:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.otp = str(random.randint(100000, 999999))
            user.save()

            # Send OTP email
            send_mail(
                subject="Portli - Your OTP Code",
                message=f"Your OTP is {user.otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=not settings.DEBUG
            )

            if settings.DEBUG:
                print(f"[REGISTER] Email: {user.email} | OTP: {user.otp} | Username: {user.username}")

            return Response({"message": "OTP sent to your email."}, status=201)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response({"error": "Email and OTP are required"}, status=400)

    try:
        user = User.objects.get(email=email.lower())
    except DoesNotExist:
        if settings.DEBUG:
            print(f"[VERIFY OTP] User not found: {email}")
        return Response({"error": "User not found"}, status=404)

    if user.otp == otp:
        user.is_verified = True
        user.otp = None
        user.save()

        if settings.DEBUG:
            print(f"[OTP VERIFIED] Email: {email} | OTP matched")

        return Response({"message": "OTP verified"}, status=200)
    else:
        if settings.DEBUG:
            print(f"[INVALID OTP] Email: {email} | Entered: {otp} | Expected: {user.otp}")
        return Response({"error": "Invalid OTP"}, status=400)



@api_view(['POST'])
def login_view(request):
    email_or_username = request.data.get('email') or request.data.get('username')
    password = request.data.get('password')

    if not email_or_username or not password:
        return Response({"message": "Email/Username and Password are required"}, status=400)

    user = User.objects(email=email_or_username.lower()).first() or \
           User.objects(username=email_or_username).first()

    if not user:
        if settings.DEBUG:
            print(f"[LOGIN FAILED] User not found: {email_or_username}")
        return Response({"message": "User not found"}, status=404)

    if not check_password(password, user.password):
        if settings.DEBUG:
            print(f"[LOGIN FAILED] Invalid password for: {email_or_username}")
        return Response({"message": "Invalid password"}, status=400)

    if not user.is_active:
        if settings.DEBUG:
            print(f"[LOGIN FAILED] Inactive account: {email_or_username}")
        return Response({"message": "Account is inactive"}, status=403)

    if not user.is_verified:
        if settings.DEBUG:
            print(f"[LOGIN FAILED] Unverified email: {email_or_username}")
        return Response({"message": "Please verify your email first"}, status=403)

    # Token auth requires a Django user instance. Since you're using MongoEngine,
    # this will likely fail unless you extend Django's `AbstractBaseUser`.
    # ❌ Token.objects.get_or_create(user=user) will raise an error
    # ✅ Suggest switching to JWT instead for compatibility, or implement custom token system.
    
    
    token = generate_jwt(user)
    return Response({
        "message": "Login successful",
        "token": token,
        "user": {
            "username": user.username,
            "email": user.email,
            "id": str(user.id),
            # "token": "JWT or custom token here"  # You’ll need a workaround here.
        }
    }, status=200)


def get_user_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects(id=payload['user_id']).first()
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# user = get_user_from_token(request)
# if not user:
#     return Response({"error": "Unauthorized"}, status=401)

# Do something with `user`



@api_view(['POST'])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=404)

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        # Send OTP to email
        send_mail(
            subject="Portli - Password Reset OTP",
            message=f"Your password reset OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=not settings.DEBUG
        )

        if settings.DEBUG:
            print(f"[FORGOT PASSWORD] OTP sent to {email}: {otp}")

        return Response({"message": "OTP sent to your email"}, status=200)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=404)

        if user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        user.set_password(new_password)
        user.otp = None  # Clear OTP after success
        user.save()

        if settings.DEBUG:
            print(f"[RESET PASSWORD] Password reset successful for {email}")

        return Response({"message": "Password has been reset successfully"}, status=200)

    return Response(serializer.errors, status=400)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    return Response({
        "message": "Welcome to your dashboard!",
        "user": {
            "username": user.username,
            "email": user.email
        }
    })