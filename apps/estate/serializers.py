from django.db import transaction
from rest_framework import serializers

from apps.ads.models import Image
from apps.common.models import Media
from apps.common.serializers import (
    MediaSerializer,
    RegionListSerializer,
    DistrictListSerializer,
    NeighborhoodListSerializer,
)
from apps.estate.models import (
    Estate,
    EstateAdvantage,
    EstateType,
    EstatePurpose,
    EstateCondition,
    EstateRepair,
    EstateQuality,
)
from apps.user.serializers import UserMiniSerializer


class EstateAdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateAdvantage
        fields = ('id', 'name')


class EstateImageSerializer(serializers.ModelSerializer):
    image = MediaSerializer(read_only=True)
    image_id = serializers.PrimaryKeyRelatedField(
        queryset=Media.objects.all(),
        source='image',
        write_only=True
    )

    class Meta:
        model = Image
        fields = ('id', 'image', 'image_id', 'is_main')


class EstateListSerializer(serializers.ModelSerializer):
    """E'lonlar ro'yxati uchun serializer"""
    user = UserMiniSerializer(read_only=True)
    region = RegionListSerializer(read_only=True)
    district = DistrictListSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    views_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = (
            'id',
            'slug',
            'title',
            'price',
            'currency',
            'currency_display',
            'type',
            'type_display',
            'purpose',
            'purpose_display',
            'room_count',
            'area',
            'floor_number',
            'floors_count',
            'region',
            'district',
            'user',
            'main_image',
            'is_vip',
            'is_top',
            'views_count',
            'likes_count',
            'created_at',
        )

    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if not main_image:
            main_image = obj.images.first()
        if main_image:
            return MediaSerializer(main_image.image).data
        return None

    def get_views_count(self, obj):
        return obj.views.count()

    def get_likes_count(self, obj):
        return obj.likes.count()


class EstateDetailSerializer(serializers.ModelSerializer):
    """E'lon tafsilotlari uchun serializer"""
    user = UserMiniSerializer(read_only=True)
    region = RegionListSerializer(read_only=True)
    district = DistrictListSerializer(read_only=True)
    neighborhood = NeighborhoodListSerializer(read_only=True)
    facilities = EstateAdvantageSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()

    type_display = serializers.CharField(source='get_type_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    repair_display = serializers.CharField(source='get_repair_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    views_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = (
            'id',
            'slug',
            'title',
            'description',
            'price',
            'currency',
            'currency_display',
            'status',
            'status_display',
            'type',
            'type_display',
            'purpose',
            'purpose_display',
            'condition',
            'condition_display',
            'repair',
            'repair_display',
            'quality',
            'quality_display',
            'room_count',
            'area',
            'floor_number',
            'floors_count',
            'facilities',
            'region',
            'district',
            'neighborhood',
            'address',
            'latitude',
            'longitude',
            'user',
            'images',
            'is_vip',
            'is_top',
            'views_count',
            'likes_count',
            'comments_count',
            'is_liked',
            'is_bookmarked',
            'created_at',
            'updated_at',
        )

    def get_images(self, obj):
        images = obj.images.select_related('image').order_by('-is_main', 'created_at')
        return EstateImageSerializer(images, many=True).data

    def get_views_count(self, obj):
        return obj.views.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmark.filter(user=request.user).exists()
        return False


class EstateCreateSerializer(serializers.ModelSerializer):
    """E'lon yaratish uchun serializer"""
    image_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    main_image_id = serializers.UUIDField(write_only=True, required=False)
    facility_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Estate
        fields = (
            'title',
            'description',
            'price',
            'currency',
            'type',
            'purpose',
            'condition',
            'repair',
            'quality',
            'room_count',
            'area',
            'floor_number',
            'floors_count',
            'country',
            'region',
            'district',
            'neighborhood',
            'address',
            'latitude',
            'longitude',
            'image_ids',
            'main_image_id',
            'facility_ids',
        )

    def validate(self, attrs):
        floor_number = attrs.get('floor_number')
        floors_count = attrs.get('floors_count')

        if floor_number and floors_count and floor_number > floors_count:
            raise serializers.ValidationError({
                'floor_number': 'Qavat raqami umumiy qavatlar sonidan katta bo\'lishi mumkin emas.'
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        image_ids = validated_data.pop('image_ids', [])
        main_image_id = validated_data.pop('main_image_id', None)
        facility_ids = validated_data.pop('facility_ids', [])

        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['slug'] = self._generate_slug(validated_data['title'])

        estate = Estate.objects.create(**validated_data)

        # Rasmlarni bog'lash
        if image_ids:
            from django.contrib.contenttypes.models import ContentType
            from apps.common.models import Project

            content_type = ContentType.objects.get_for_model(Estate)
            for idx, image_id in enumerate(image_ids):
                Image.objects.create(
                    user=user,
                    project=Project.ESTATE,
                    content_type=content_type,
                    object_id=estate.id,
                    image_id=image_id,
                    is_main=(str(image_id) == str(main_image_id)) if main_image_id else (idx == 0)
                )

        # Qulayliklarni bog'lash
        if facility_ids:
            facilities = EstateAdvantage.objects.filter(id__in=facility_ids)
            estate.facilities.set(facilities)

        return estate

    def _generate_slug(self, title):
        from django.utils.text import slugify
        import uuid
        base_slug = slugify(title, allow_unicode=True)
        return f"{base_slug}-{uuid.uuid4().hex[:8]}"


class EstateUpdateSerializer(serializers.ModelSerializer):
    """E'lonni yangilash uchun serializer"""
    image_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    main_image_id = serializers.UUIDField(write_only=True, required=False)
    facility_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Estate
        fields = (
            'title',
            'description',
            'price',
            'currency',
            'type',
            'purpose',
            'condition',
            'repair',
            'quality',
            'room_count',
            'area',
            'floor_number',
            'floors_count',
            'country',
            'region',
            'district',
            'neighborhood',
            'address',
            'latitude',
            'longitude',
            'image_ids',
            'main_image_id',
            'facility_ids',
        )

    def validate(self, attrs):
        floor_number = attrs.get('floor_number', self.instance.floor_number if self.instance else None)
        floors_count = attrs.get('floors_count', self.instance.floors_count if self.instance else None)

        if floor_number and floors_count and floor_number > floors_count:
            raise serializers.ValidationError({
                'floor_number': 'Qavat raqami umumiy qavatlar sonidan katta bo\'lishi mumkin emas.'
            })

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        image_ids = validated_data.pop('image_ids', None)
        main_image_id = validated_data.pop('main_image_id', None)
        facility_ids = validated_data.pop('facility_ids', None)

        # Asosiy ma'lumotlarni yangilash
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Rasmlarni yangilash
        if image_ids is not None:
            from django.contrib.contenttypes.models import ContentType
            from apps.common.models import Project

            # Eski rasmlarni o'chirish
            instance.images.all().delete()

            content_type = ContentType.objects.get_for_model(Estate)
            for idx, image_id in enumerate(image_ids):
                Image.objects.create(
                    user=instance.user,
                    project=Project.ESTATE,
                    content_type=content_type,
                    object_id=instance.id,
                    image_id=image_id,
                    is_main=(str(image_id) == str(main_image_id)) if main_image_id else (idx == 0)
                )

        # Qulayliklarni yangilash
        if facility_ids is not None:
            facilities = EstateAdvantage.objects.filter(id__in=facility_ids)
            instance.facilities.set(facilities)

        return instance
