from django.db.models import Count, Q
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from apps.ads.models import AdsStatus
from apps.estate.models import Estate, EstateAdvantage, EstateType, EstatePurpose
from apps.estate.serializers import (
    EstateListSerializer,
    EstateDetailSerializer,
    EstateCreateSerializer,
    EstateUpdateSerializer,
    EstateAdvantageSerializer,
)


class EstateFilter(filters.FilterSet):
    """Estate uchun filter"""
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_area = filters.NumberFilter(field_name='area', lookup_expr='gte')
    max_area = filters.NumberFilter(field_name='area', lookup_expr='lte')
    min_rooms = filters.NumberFilter(field_name='room_count', lookup_expr='gte')
    max_rooms = filters.NumberFilter(field_name='room_count', lookup_expr='lte')
    min_floor = filters.NumberFilter(field_name='floor_number', lookup_expr='gte')
    max_floor = filters.NumberFilter(field_name='floor_number', lookup_expr='lte')
    facilities = filters.BaseInFilter(field_name='facilities__id')

    class Meta:
        model = Estate
        fields = [
            'type',
            'purpose',
            'condition',
            'repair',
            'quality',
            'currency',
            'region',
            'district',
            'neighborhood',
            'is_vip',
            'is_top',
            'room_count',
        ]


class EstateViewSet(viewsets.ModelViewSet):
    """
    Estate CRUD ViewSet

    list: E'lonlar ro'yxati (faqat aktiv)
    retrieve: E'lon tafsilotlari
    create: Yangi e'lon yaratish (auth required)
    update: E'lonni yangilash (faqat egasi)
    destroy: E'lonni o'chirish (faqat egasi)
    """
    queryset = Estate.objects.select_related(
        'user', 'region', 'district', 'neighborhood'
    ).prefetch_related(
        'images', 'facilities', 'likes', 'views', 'comments'
    )
    filterset_class = EstateFilter
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'area', 'room_count', 'created_at']
    ordering = ['-is_vip', '-is_top', '-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_estates']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'list':
            return EstateListSerializer
        elif self.action == 'retrieve':
            return EstateDetailSerializer
        elif self.action == 'create':
            return EstateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EstateUpdateSerializer
        return EstateListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Faqat aktiv e'lonlarni ko'rsatish (my_estates dan tashqari)
        if self.action == 'list':
            queryset = queryset.filter(status=AdsStatus.ACTIVE)
        elif self.action == 'my_estates':
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Ko'rishlar sonini oshirish
        if request.user.is_authenticated:
            from django.contrib.contenttypes.models import ContentType
            from apps.ads.models import View
            from apps.common.models import Project

            content_type = ContentType.objects.get_for_model(Estate)
            View.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=instance.id,
                defaults={
                    'project': Project.ESTATE,
                    'ip_address': self._get_client_ip(request)
                }
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # Faqat egasi o'chira oladi
        if instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Siz bu e'lonni o'chira olmaysiz.")
        instance.delete()

    def perform_update(self, serializer):
        # Faqat egasi yangilay oladi
        if serializer.instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Siz bu e'lonni yangilay olmaysiz.")
        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_estates(self, request):
        """Foydalanuvchining o'z e'lonlari"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EstateListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = EstateListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """E'lonni yoqtirish/yoqtirmaslik"""
        from django.contrib.contenttypes.models import ContentType
        from apps.ads.models import Like
        from apps.common.models import Project

        estate = self.get_object()
        content_type = ContentType.objects.get_for_model(Estate)

        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=estate.id,
            defaults={'project': Project.ESTATE}
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': estate.likes.count()})

        return Response({'status': 'liked', 'likes_count': estate.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """E'lonni saqlash/o'chirish"""
        from django.contrib.contenttypes.models import ContentType
        from apps.ads.models import Bookmark
        from apps.common.models import Project

        estate = self.get_object()
        content_type = ContentType.objects.get_for_model(Estate)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=estate.id,
            defaults={'project': Project.ESTATE}
        )

        if not created:
            bookmark.delete()
            return Response({'status': 'removed'})

        return Response({'status': 'saved'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def bookmarks(self, request):
        """Saqlangan e'lonlar"""
        from django.contrib.contenttypes.models import ContentType
        from apps.ads.models import Bookmark

        content_type = ContentType.objects.get_for_model(Estate)
        bookmarked_ids = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type
        ).values_list('object_id', flat=True)

        queryset = self.get_queryset().filter(id__in=bookmarked_ids)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EstateListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = EstateListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """E'lonni shikoyat qilish"""
        from django.contrib.contenttypes.models import ContentType
        from apps.ads.models import Report, ReportReason
        from apps.common.models import Project

        estate = self.get_object()
        content_type = ContentType.objects.get_for_model(Estate)

        reason = request.data.get('reason', ReportReason.OTHER)
        description = request.data.get('description', '')

        report, created = Report.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=estate.id,
            defaults={
                'project': Project.ESTATE,
                'reason': reason,
                'description': description
            }
        )

        if not created:
            return Response(
                {'detail': 'Siz bu e\'longa allaqachon shikoyat qilgansiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'status': 'reported'})

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class EstateAdvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """Qulayliklar ro'yxati"""
    queryset = EstateAdvantage.objects.all()
    serializer_class = EstateAdvantageSerializer
    permission_classes = [AllowAny]
    pagination_class = None
