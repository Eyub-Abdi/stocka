import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stocka.settings')

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

EMAIL = "ayubabdiy@gmail.com"
PASSWORD = "myungsoon"

username_field = getattr(User, 'USERNAME_FIELD', 'username')

fields = {username_field: EMAIL}
if 'email' in [f.name for f in User._meta.fields]:
    fields['email'] = EMAIL

user, created = User.objects.get_or_create(**{username_field: EMAIL}, defaults=fields)
if created:
    user.set_password(PASSWORD)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Superuser created.")
else:
    user.is_superuser = True
    user.is_staff = True
    user.set_password(PASSWORD)
    user.save()
    print("Superuser updated.")
