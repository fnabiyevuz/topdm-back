from django.urls import path

from apps.common import views

app_name = "common"

urlpatterns = [
    path("country/", views.CountryListView.as_view(), name="country"),
    path("region/", views.RegionListView.as_view(), name="region"),
    path("district/", views.DistrictListView.as_view(), name="district"),
    path("neighborhood/", views.NeighborhoodListView.as_view(), name="neighborhood"),

    path('media/create/', views.MediaCreateAPIView.as_view(), name='media-create'),

    # health checks
]
