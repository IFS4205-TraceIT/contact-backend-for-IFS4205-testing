from django.contrib import admin

# Register your models here.

from .models import (
    Buildings,
    Buildingaccess
)
# Register your models here.
@admin.register(Buildingaccess, Buildings)
class BuildingAdmin(admin.ModelAdmin):
    pass