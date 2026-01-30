from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.ads.models import Comment
from apps.ads.serializers import CommentSerializer, CommentCreateSerializer
from apps.common.models import Project


class CommentViewSet(viewsets.ModelViewSet):
    """
    Izohlar ViewSet

    list: E'lonning barcha izohlari
    create: Yangi izoh qo'shish
    destroy: Izohni o'chirish (faqat egasi)
    """
    queryset = Comment.objects.select_related('user').prefetch_related('replies')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by content_type and object_id
        content_type_id = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type_id and object_id:
            queryset = queryset.filter(
                content_type_id=content_type_id,
                object_id=object_id,
                parent__isnull=True  # Faqat asosiy izohlar
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_type_id = request.data.get('content_type')
        object_id = request.data.get('object_id')

        if not content_type_id or not object_id:
            return Response(
                {'detail': 'content_type va object_id majburiy.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            return Response(
                {'detail': 'Noto\'g\'ri content_type.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = Comment.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            project=self._get_project_from_content_type(content_type),
            **serializer.validated_data
        )

        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Siz bu izohni o'chira olmaysiz.")
        instance.delete()

    def _get_project_from_content_type(self, content_type):
        model_project_map = {
            'estate': Project.ESTATE,
        }
        return model_project_map.get(content_type.model, Project.ESTATE)
