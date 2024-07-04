from django.urls import re_path
from .import views

urlpatterns = [
    re_path(r'^api/nearby-locations$', views.nearby_location_list),
    re_path(r'^api/location-detail$', views.location_detail_view),
    re_path(r'^api/get-weather-status$', views.weather_status)
]
