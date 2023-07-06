from django.contrib import admin

from users.models import User


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.get_fields()][1:13]
    search_fields = ("username",)


admin.site.register(User, UserAdmin)
