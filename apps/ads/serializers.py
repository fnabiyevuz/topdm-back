from rest_framework import serializers

from apps.ads.models import Comment, Image, Like, Bookmark, Report, Rating
from apps.common.serializers import MediaSerializer
from apps.user.serializers import UserMiniSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Izoh serializer"""
    user = UserMiniSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'parent',
            'comment',
            'replies',
            'replies_count',
            'created_at',
        )
        read_only_fields = ('id', 'user', 'created_at')

    def get_replies(self, obj):
        # Faqat birinchi darajali izohlar uchun javoblarni ko'rsatish
        if obj.parent is None:
            replies = obj.replies.select_related('user').all()[:5]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []

    def get_replies_count(self, obj):
        return obj.replies.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """Izoh yaratish serializer"""

    class Meta:
        model = Comment
        fields = ('parent', 'comment')

    def validate_parent(self, value):
        if value and value.parent:
            raise serializers.ValidationError("Faqat asosiy izohlarga javob yozish mumkin.")
        return value


class ImageSerializer(serializers.ModelSerializer):
    """Rasm serializer"""
    image = MediaSerializer(read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'image', 'is_main')


class RatingSerializer(serializers.ModelSerializer):
    """Reyting serializer"""
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'user', 'rating', 'created_at')


class RatingCreateSerializer(serializers.ModelSerializer):
    """Reyting yaratish serializer"""

    class Meta:
        model = Rating
        fields = ('rating',)
