from django.contrib.auth.backends import ModelBackend
from .models import Usuario


class EmailOrUsernameBackend(ModelBackend):
    """Autentica tanto por e-mail quanto por username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Tenta por e-mail primeiro
        try:
            user = Usuario.objects.get(email__iexact=username.strip())
        except Usuario.DoesNotExist:
            # Tenta por username
            try:
                user = Usuario.objects.get(username__iexact=username.strip())
            except Usuario.DoesNotExist:
                return None
        except Usuario.MultipleObjectsReturned:
            # E-mail duplicado — tenta username como fallback
            try:
                user = Usuario.objects.get(username__iexact=username.strip())
            except Usuario.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
