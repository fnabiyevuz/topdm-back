from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views

router = DefaultRouter()
# router.register(r'user', views.UserViewSet, basename='user')
# router.register(r'devices', views.UserDeviceViewSet, basename='userdevice')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
