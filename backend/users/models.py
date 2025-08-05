from mongoengine import Document, StringField, BooleanField, EmailField, DateTimeField
from django.contrib.auth.hashers import make_password, check_password
import datetime

class UserManager:
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = User(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

    @staticmethod
    def normalize_email(email):
        """
        Normalize the email address by lowercasing the domain part.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            return email.lower()
        else:
            return email_name.lower() + '@' + domain_part.lower()


class User(Document):
    email = EmailField(required=True, unique=True)
    username = StringField(max_length=50, required=True, unique=True, sparse=True)
    full_name = StringField(max_length=100, required=True)
    password = StringField(required=True)  # Hashed password

    is_verified = BooleanField(default=False)
    otp = StringField(max_length=6, blank=True, null=True)
    otp_expiry = DateTimeField(null=True)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    last_login = StringField(default=None)
    date_joined = StringField(default=lambda: datetime.datetime.utcnow().isoformat())

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    user_manager = UserManager()

    meta = {

        'indexes': [
            {'fields': ['email'], 'unique': True},
            {'fields': ['username'], 'unique': True}
        ],
        'strict': False
    }

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        return self

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
