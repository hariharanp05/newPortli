# backend/users/utils.py
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

def generate_tokens_for_user(user, access_lifetime_minutes=15):
    """
    Return dict {access, refresh} where both are strings.
    We do NOT call RefreshToken.for_user(user) (requires Django ORM user).
    Instead we create RefreshToken() and set claims manually.
    """
    refresh = RefreshToken()
    # Put claims we need (user_id must match MongoEngine id string)
    refresh["user_id"] = str(user.id)
    refresh["email"] = getattr(user, "email", "")
    refresh["username"] = getattr(user, "username", "")

    access = refresh.access_token
    # Optionally set a custom access lifetime
    if access_lifetime_minutes:
        access.set_exp(lifetime=timedelta(minutes=access_lifetime_minutes))

    return {
        "refresh": str(refresh),
        "access": str(access),
    }
