from django.db import transaction

from rest_framework import serializers

from events.models import Event

from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(
        source="participant.username", read_only=True
    )
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Registration
        fields = [
            "id",
            "event",
            "event_title",
            "participant",
            "participant_username",
            "is_cancelled",
            "created_at",
        ]
        read_only_fields = ["participant", "is_cancelled", "created_at"]

    def validate_event(self, event):

        if event.status != Event.Status.PUBLISHED:
            raise serializers.ValidationError(
                "You can only register for published events."
            )
        return event

    def validate(self, attrs):

        request = self.context["request"]
        event = attrs["event"]

        if Registration.objects.filter(
            participant=request.user, event=event, is_cancelled=False
        ).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )

        if event.seats_left <= 0:
            raise serializers.ValidationError("This event is already full.")

        return attrs

    def create(self, validated_data):

        request = self.context["request"]
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=validated_data["event"].pk)
            if Registration.objects.filter(
                participant=request.user, event=event, is_cancelled=False
            ).exists():
                raise serializers.ValidationError(
                    {"event": "You are already registered for this event."}
                )
            if event.seats_left <= 0:
                raise serializers.ValidationError(
                    {"event": "This event is already full."}
                )
            validated_data["participant"] = request.user
            validated_data["event"] = event
            return super().create(validated_data)
