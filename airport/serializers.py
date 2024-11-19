from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    Crew,
    Airplane, Airport, Route,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name"
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity"
        )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "name",
            "closest_big_city"
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "source",
            "destination",
            "distance"
        )


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
