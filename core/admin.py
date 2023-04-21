from django.contrib import admin
from core.models import Holding, Organization, Department, MOL, Property, InventoryList


class HoldingAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name",)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "holding")
    search_fields = ("name",)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "floor", "cabinet", "organization")
    search_fields = ("name",)


class MOLAdmin(admin.ModelAdmin):
    list_display = ("FIO", "phone_num", "department", "post")
    search_fields = ("FIO",)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "u_m", "description")
    search_fields = ("name",)


class InventoryListAdmin(admin.ModelAdmin):
    list_display = ("invent_num", "serial_num", "amount", "account_date", "MOL", "property", "description")
    search_fields = ("invent_num",)


admin.site.register(Holding, HoldingAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(MOL, MOLAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(InventoryList, InventoryListAdmin)

# readonly_fields = ('id',)
# Register your models here.
