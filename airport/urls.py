from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    CrewViewSet,
    AirplaneViewSet,
)

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
