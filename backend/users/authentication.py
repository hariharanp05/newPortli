# backend/users/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from .models import User  # MongoEngine model

class MongoJWTAuthentication(JWTAuthentication):
    """
    Validate the token using SimpleJWT machinery (JWTAuthentication),
    but fetch the user from MongoEngine instead of Django ORM.
    """

    def get_user(self, validated_token):
        # api_settings.USER_ID_CLAIM is typically 'user_id'
        claim_name = api_settings.USER_ID_CLAIM
        user_id = validated_token.get(claim_name)

        if user_id is None:
            raise AuthenticationFailed("Token contained no recognizable user identification", code="no_user_id")

        # Query MongoEngine user by string id
        user = User.objects(id=str(user_id)).first()
        if user is None:
            raise AuthenticationFailed("User not found", code="user_not_found")

        return user
