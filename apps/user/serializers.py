from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.common.serializers import MediaSerializer, RegionListSerializer, DistrictListSerializer
from apps.user.models import User


class UserMiniSerializer(serializers.ModelSerializer):
    """Foydalanuvchi qisqacha ma'lumotlari"""
    avatar = MediaSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username', 'first_name', 'last_name', 'middle_name', 'role')


class UserDetailSerializer(serializers.ModelSerializer):
    """Foydalanuvchi to'liq ma'lumotlari"""
    avatar = MediaSerializer(read_only=True)
    region = RegionListSerializer(read_only=True)
    district = DistrictListSerializer(read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    ads_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'avatar',
            'primary_phone',
            'secondary_phone',
            'birth_date',
            'gender',
            'gender_display',
            'role',
            'role_display',
            'region',
            'district',
            'bio',
            'tg_username',
            'ads_count',
            'average_rating',
            'created_at',
        )

    def get_ads_count(self, obj):
        return obj.ads.filter(is_deleted=False).count()

    def get_average_rating(self, obj):
        from django.db.models import Avg
        avg = obj.rating.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else None


class UserRegisterSerializer(serializers.ModelSerializer):
    """Ro'yxatdan o'tish serializer"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'primary_phone',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Parollar mos kelmaydi.'
            })
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Bu username allaqachon band.')
        return value.lower()

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Bu email allaqachon ro\'yxatdan o\'tgan.')
        return value.lower() if value else value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Profil yangilash serializer"""
    avatar_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'middle_name',
            'avatar_id',
            'primary_phone',
            'secondary_phone',
            'birth_date',
            'gender',
            'region',
            'district',
            'bio',
            'tg_username',
        )

    def update(self, instance, validated_data):
        avatar_id = validated_data.pop('avatar_id', None)

        if avatar_id is not None:
            from apps.common.models import Media
            try:
                instance.avatar = Media.objects.get(id=avatar_id)
            except Media.DoesNotExist:
                pass
        elif avatar_id is None and 'avatar_id' in self.initial_data:
            instance.avatar = None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Parol o'zgartirish serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Yangi parollar mos kelmaydi.'
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Joriy parol noto\'g\'ri.')
        return value
