from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):

    # Main Event model.

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CLOSED = "CLOSED", "Closed"
        FINISHED = "FINISHED", "Finished"

    # Legal transitions between statuses (from -> allowed set of "to")
    ALLOWED_TRANSITIONS = {
        Status.DRAFT: {Status.PUBLISHED},
        Status.PUBLISHED: {Status.DRAFT, Status.CLOSED},
        Status.CLOSED: {Status.PUBLISHED, Status.FINISHED},
        Status.FINISHED: set(),  # final state, no way back
    }

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(
        help_text="Max number of participants for the whole event"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    # Set to True by the organizer once results have been published.
    results_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def change_status(self, new_status):
        """Change status if the transition is legal, otherwise raise an error."""
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot move event from '{self.status}' to '{new_status}'."
            )
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])

    @property
    def seats_taken(self):
        return self.registrations.filter(is_cancelled=False).count()

    @property
    def seats_left(self):
        return max(self.capacity - self.seats_taken, 0)


class EventStage(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="stages")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(
        help_text="Position of this stage inside the event, starting at 1"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ["order"]
        unique_together = ("event", "order")

    def __str__(self):
        return f"{self.event.title} - Stage {self.order}: {self.title}"


class StageRole(models.Model):
    class RoleType(models.TextChoices):
        SPEAKER = "SPEAKER", "Speaker"
        JUDGE = "JUDGE", "Judge"
        MENTOR = "MENTOR", "Mentor"

    stage = models.ForeignKey(
        EventStage, on_delete=models.CASCADE, related_name="stage_roles"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stage_roles"
    )
    role_type = models.CharField(max_length=20, choices=RoleType.choices)

    class Meta:
        unique_together = ("stage", "user", "role_type")

    def __str__(self):
        return f"{self.user.username} as {self.role_type} in {self.stage}"


class Attribute(models.Model):
    class DataType(models.TextChoices):
        TEXT = "TEXT", "Text"
        NUMBER = "NUMBER", "Number"
        BOOLEAN = "BOOLEAN", "Boolean"
        DATE = "DATE", "Date"

    key = models.SlugField(
        max_length=100, unique=True, help_text="Unique code, e.g. 'num_rounds'"
    )
    label = models.CharField(
        max_length=150, help_text="Human friendly name, e.g. 'Number of rounds'"
    )
    data_type = models.CharField(max_length=20, choices=DataType.choices)

    def __str__(self):
        return f"{self.label} ({self.data_type})"


class EventAttributeValue(models.Model):

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="attribute_values"
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="values"
    )

    value_text = models.CharField(max_length=500, null=True, blank=True)
    value_number = models.FloatField(null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("event", "attribute")

    def clean(self):
        # Make sure only the field matching the attribute's data type is used.
        type_to_field = {
            Attribute.DataType.TEXT: "value_text",
            Attribute.DataType.NUMBER: "value_number",
            Attribute.DataType.BOOLEAN: "value_boolean",
            Attribute.DataType.DATE: "value_date",
        }
        expected_field = type_to_field[self.attribute.data_type]
        if getattr(self, expected_field) is None:
            raise ValidationError(
                f"'{expected_field}' must be set for attribute type {self.attribute.data_type}."
            )

    @property
    def value(self):
        """Return whichever typed value is actually set."""
        for field in ("value_text", "value_number", "value_boolean", "value_date"):
            v = getattr(self, field)
            if v is not None:
                return v
        return None

    def __str__(self):
        return f"{self.event.title} / {self.attribute.key} = {self.value}"
