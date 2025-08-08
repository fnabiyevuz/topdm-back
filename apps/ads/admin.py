from django.contrib import admin

from .models import Image, Comment, Like, View, Bookmark, Report


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'image', 'created_at')
    search_fields = ('content_type__model',)
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'text', 'created_at')
    search_fields = ('text', 'user__first_name', 'user__last_name')
    list_filter = ('created_at',)
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object


@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'reason', 'created_at')
    search_fields = ('reason',)
    readonly_fields = ('content_object',)

    def content_object(self, obj):
        return obj.content_object
