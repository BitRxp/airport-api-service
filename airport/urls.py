from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    CrewViewSet,
    AirplaneViewSet,
    AirportViewSet, RouteViewSet,
)

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
