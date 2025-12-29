from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class UsernameOrEmailBackend(ModelBackend):
    """Authenticate against either username or email.

    This works with Django auth and SimpleJWT since they both call
    `authenticate(username=..., password=...)`. The `username` value
    may actually be a username or an email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        # Try matching either username or email (case-insensitive)
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.MultipleObjectsReturned:
            user = (
                UserModel.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                .order_by("id")
                .first()
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to mitigate timing attacks
            dummy = UserModel()
            dummy.set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
