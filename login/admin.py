from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    """ Admin : User"""
    list_display = ('email', 'first_name', 'last_name', 'last_login')


admin.site.register(User, UserAdmin)
