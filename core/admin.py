from django.contrib import admin
from core.models import Holding, Organization, Department, Mol, Property, InventoryList, Operation


class HoldingAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name",)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "holding")
    search_fields = ("name",)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "floor", "cabinet", "organization")
    search_fields = ("name",)


class MolAdmin(admin.ModelAdmin):
    list_display = ("FIO", "phone_num", "department", "post")
    search_fields = ("FIO",)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "u_m", "description")
    search_fields = ("name",)


class InventoryListAdmin(admin.ModelAdmin):
    list_display = ("invent_num", "serial_num", "amount", "account_date", "mol", "property", "description")
    search_fields = ("invent_num",)


class OperationAdmin(admin.ModelAdmin):
    list_display = ("inventory_list", "data_time", "waybill", "fromm", "to", "type")
    search_fields = ("inventory_list",)


admin.site.register(Holding, HoldingAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Mol, MolAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Operation, OperationAdmin)
admin.site.register(InventoryList, InventoryListAdmin)



# readonly_fields = ('id',)
# Register your models here.
