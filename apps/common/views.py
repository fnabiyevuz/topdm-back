import redis
from celery import Celery
from celery.exceptions import OperationalError
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.common import serializers as com_ser
from apps.common.models import Country, Region, District, Neighborhood, Media

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure Redis connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


@api_view(["GET"])
def health_check_redis(request):
    try:
        # Check Redis connection
        redis_client.ping()
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    except redis.ConnectionError:
        return Response(
            {"status": "error", "message": "Redis server is not working."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def health_check_celery(request):
    try:
        # Ping Celery workers
        response = app.control.ping()
        if response:
            return Response(
                {"status": "success", "workers": response}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": "error", "message": "No Celery workers responded."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except OperationalError:
        return Response(
            {"status": "error", "message": "Celery OperationalError occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class CountryListView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = com_ser.CountryListSerializer
    search_fields = ('name',)


class RegionListView(ListAPIView):
    queryset = Region.objects.all()
    serializer_class = com_ser.RegionListSerializer
    filterset_fields = ("country",)
    search_fields = ('name',)


class DistrictListView(ListAPIView):
    queryset = District.objects.all()
    serializer_class = com_ser.DistrictListSerializer
    filterset_fields = ("region",)
    search_fields = ('name',)


class NeighborhoodListView(ListAPIView):
    queryset = Neighborhood.objects.all()
    serializer_class = com_ser.NeighborhoodListSerializer
    filterset_fields = ("district",)
    search_fields = ('name',)


class MediaCreateAPIView(CreateAPIView):
    queryset = Media.objects.all()
    serializer_class = com_ser.MediaSerializer
    parser_classes = (MultiPartParser, FormParser)
