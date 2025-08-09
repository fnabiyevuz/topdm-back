from django.urls import path, include

urlpatterns = [
    path('common/', include('apps.common.urls'), name='common'),
    path('user/', include('apps.user.urls'), name='user'),
]
