from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.estate.views import EstateViewSet, EstateAdvantageViewSet

router = DefaultRouter()
router.register(r'estates', EstateViewSet, basename='estate')
router.register(r'advantages', EstateAdvantageViewSet, basename='advantage')

urlpatterns = [
    path('', include(router.urls)),
]
