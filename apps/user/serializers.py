from rest_framework import serializers

from apps.common.serializers import MediaSerializer
from apps.user.models import User


class UserMiniSerializer(serializers.ModelSerializer):
    avatar = MediaSerializer()

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username', 'first_name', 'last_name', 'middle_name', 'role')
