from django.db import models
from rest_framework.exceptions import ValidationError

from django.conf import settings


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType,
                                      on_delete=models.CASCADE
                                      )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport,
                               on_delete=models.CASCADE,
                               related_name="routes_as_source"
                               )
    destination = models.ForeignKey(Airport,
                                    on_delete=models.CASCADE,
                                    related_name="routes_as_destination"
                                    )
    distance = models.IntegerField()

    def __str__(self):
        return self.source.name + " - " + self.destination.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Flight(models.Model):
    route = models.ForeignKey(Route,
                              on_delete=models.CASCADE
                              )
    airplane = models.ForeignKey(Airplane,
                                 on_delete=models.CASCADE
                                 )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.route.destination} - {self.departure_time}"

    @staticmethod
    def validate_flight_departure_location(
            source,
            previous_destination,
            available_route_list,
            error_to_raise
    ):
        if source != previous_destination:
            if available_route_list:
                raise error_to_raise(
                    "Departure location should match the arrival location "
                    "of the previous flight. "
                    f"Available routes with the correct departure location: "
                    f"{available_route_list}."
                )
            else:
                raise error_to_raise(
                    "Departure location should match the arrival location "
                    "of the previous flight. "
                    "There are no routes with the correct departure location. "
                    "You need to create a route first, "
                    "then schedule the flight."
                )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight,
                               on_delete=models.CASCADE
                               )
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE
                              )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    @staticmethod
    def validate_ticket_flight(
            order_created_at,
            flight_departure_time,
            error_to_raise
    ):
        if order_created_at > flight_departure_time:
            raise error_to_raise(
                {
                    "order": "Booking for past flights is not available. "
                             f"Order created at {order_created_at} "
                             f"but the flight departs at "
                             f"{flight_departure_time}."
                }
            )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
