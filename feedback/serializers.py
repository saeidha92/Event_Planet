from rest_framework import serializers

from events.models import Event
from registrations.models import Registration

from .models import Feedback, Result


class FeedbackSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(
        source="participant.username", read_only=True
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "event",
            "participant",
            "participant_username",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["participant", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        event = attrs["event"]

        registered = Registration.objects.filter(
            participant=request.user, event=event, is_cancelled=False
        ).exists()
        if not registered:
            raise serializers.ValidationError(
                "You must be registered for this event to leave feedback."
            )

        # Rule: only allowed once the event has FINISHED.
        if event.status != Event.Status.FINISHED:
            raise serializers.ValidationError(
                "Feedback is only allowed after the event has finished."
            )

        # One feedback per participant per event.
        if Feedback.objects.filter(participant=request.user, event=event).exists():
            raise serializers.ValidationError(
                "You already submitted feedback for this event."
            )

        return attrs

    def create(self, validated_data):
        validated_data["participant"] = self.context["request"].user
        return super().create(validated_data)


class ResultSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(
        source="participant.username", read_only=True
    )

    class Meta:
        model = Result
        fields = [
            "id",
            "event",
            "participant",
            "participant_username",
            "rank",
            "score",
            "note",
        ]
        read_only_fields = ["event"]
