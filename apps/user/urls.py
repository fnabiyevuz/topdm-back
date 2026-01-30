from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.user import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    # Auth
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<uuid:id>/', views.UserPublicProfileView.as_view(), name='public_profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
]
