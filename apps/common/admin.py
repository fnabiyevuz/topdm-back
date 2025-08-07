from django.contrib import admin

from .models import Country, Region, District, Neighborhood, Media


@admin.action(description="Restore selected objects")
def restore_objects(modeladmin, request, queryset):
    queryset.update(is_deleted=False)


class SoftDeleteAdminMixin(admin.ModelAdmin):
    """
    Admin panelda barcha obyektlar (deleted va active) ko‘rinadi,
    lekin delete action soft delete qiladi.
    """

    actions = (restore_objects,)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

    def delete_model(self, request, obj):
        obj.delete()

    # Ixtiyoriy: filter qo‘shib qo‘ysang yaxshi bo‘ladi
    list_filter = ('is_deleted',)


@admin.register(Country)
class CountryAdmin(SoftDeleteAdminMixin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)


@admin.register(Region)
class RegionAdmin(SoftDeleteAdminMixin):
    list_display = ("name", "country", "is_active", "created_at")
    search_fields = ("name", "country__name")
    list_filter = ("country", "is_active", "created_at")
    ordering = ("-created_at",)
    autocomplete_fields = ("country",)


@admin.register(District)
class DistrictAdmin(SoftDeleteAdminMixin):
    list_display = ("name", "region", "is_active", "created_at")
    search_fields = ("name", "region__name", "region__country__name")
    list_filter = ("region", "is_active", "created_at")
    ordering = ("-created_at",)
    autocomplete_fields = ("region",)


@admin.register(Neighborhood)
class NeighborhoodAdmin(SoftDeleteAdminMixin):
    list_display = ("name", "district", "is_active", "created_at")
    search_fields = ("name", "district__name", "district__region__name")
    list_filter = ("district", "is_active", "created_at")
    ordering = ("-created_at",)
    autocomplete_fields = ("district",)


@admin.register(Media)
class MediaAdmin(SoftDeleteAdminMixin):
    list_display = ("file_name", "file_type", "created_at", "is_active")
    search_fields = ("file_name",)
    list_filter = ("file_type", "created_at", "is_active")
    readonly_fields = ("file_type", "file_name")
    ordering = ("-created_at",)
