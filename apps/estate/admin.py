from django.contrib import admin

from apps.ads.models import Ads


# @admin.register(Ads)
# class AdsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'user', 'created_at', 'is_active')
#     search_fields = ('title', 'description')
#     list_filter = ('created_at', 'is_active')
