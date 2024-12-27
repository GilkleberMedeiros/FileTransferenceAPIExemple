from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin # type: ignore
from .models import User

admin.site.register(User, UserAdmin)
