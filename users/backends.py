from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q


class CustomAuthBackend(BaseBackend):
    def authenticate(self, email=None, password=None):
        try:
            user = get_user_model().objects.get(Q(email=email))
        except get_user_model().DoesNotExist:
            return None

        if getattr(user, 'is_active') and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
