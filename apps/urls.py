from django.urls import path, include

urlpatterns = [
    path('common/', include('apps.common.urls'), name='common'),
    path('user/', include('apps.user.urls'), name='user'),
    path('estate/', include('apps.estate.urls'), name='estate'),
    path('ads/', include('apps.ads.urls'), name='ads'),
]
