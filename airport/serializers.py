from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    Crew,
    Airplane, Airport, Route, Order, Ticket, Flight,
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


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )

    def validate(self, data):
        airplane = data.get("airplane")
        route = data.get("route")
        departure_time = data.get("departure_time")
        arrival_time = data.get("arrival_time")

        previous_flight = (
            Flight.objects
            .filter(airplane=airplane)
            .order_by("-arrival_time")
            .first()
        )
        previous_arrival_time = None

        if previous_flight:
            previous_arrival_time = previous_flight.arrival_time

            available_routes = Route.objects.filter(
                source=previous_flight.route.destination
            )
            available_route_list = None
            if available_routes:
                available_route_list = ", ".join(
                    [route.full_route for route in available_routes]
                )

            Flight.validate_flight_departure_location(
                route.source,
                previous_flight.route.destination,
                available_route_list,
                ValidationError
            )


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(source="route.source", read_only=True)
    destination = serializers.CharField(source="route.destination", read_only=True)
    airplane_name = serializers.CharField(
        source="airplane.name",
        read_only=True,
    )
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity",
        read_only=True,
    )
    ticket_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane_name",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "airplane_capacity",
            "ticket_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightSerializer()


class TicketSeatSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    taken_places = TicketSeatSerializer(source="tickets", many=True, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "airplane",
            "taken_places",
            "crew"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
