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
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country__name")
    list_filter = ("country",)
    ordering = ("name",)
    autocomplete_fields = ("country",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name", "region__name", "region__country__name")
    list_filter = ("region",)
    ordering = ("name",)
    autocomplete_fields = ("region",)


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    search_fields = ("name", "district__name", "district__region__name")
    list_filter = ("district",)
    ordering = ("name",)
    autocomplete_fields = ("district",)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("file_name", "file_type")
    search_fields = ("file_name",)
    list_filter = ("file_type",)
    readonly_fields = ("file_type", "file_name")
