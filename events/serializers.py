from rest_framework import serializers

from .models import Attribute, Event, EventAttributeValue, EventStage, StageRole


class StageRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = StageRole
        fields = ["id", "stage", "user", "username", "role_type"]
        read_only_fields = ["stage"]


class EventStageSerializer(serializers.ModelSerializer):
    roles = StageRoleSerializer(source="stage_roles", many=True, read_only=True)

    class Meta:
        model = EventStage
        fields = [
            "id",
            "event",
            "title",
            "description",
            "order",
            "start_time",
            "end_time",
            "roles",
        ]
        read_only_fields = ["event"]

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )
        return attrs


class AttributeSerializer(serializers.ModelSerializer):
    """Attribute definitions are shared metadata, reusable across events."""

    class Meta:
        model = Attribute
        fields = ["id", "key", "label", "data_type"]


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_key = serializers.CharField(source="attribute.key", read_only=True)
    attribute_label = serializers.CharField(source="attribute.label", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = EventAttributeValue
        fields = [
            "id",
            "event",
            "attribute",
            "attribute_key",
            "attribute_label",
            "data_type",
            "value_text",
            "value_number",
            "value_boolean",
            "value_date",
            "value",
        ]
        read_only_fields = ["event"]

    def get_value(self, obj):
        return obj.value

    def validate(self, attrs):
        # Reuse the model's clean() logic so type-safety is enforced here too.
        attribute = attrs.get("attribute") or getattr(self.instance, "attribute", None)
        type_to_field = {
            Attribute.DataType.TEXT: "value_text",
            Attribute.DataType.NUMBER: "value_number",
            Attribute.DataType.BOOLEAN: "value_boolean",
            Attribute.DataType.DATE: "value_date",
        }
        expected_field = type_to_field[attribute.data_type]
        if attrs.get(expected_field) is None and not (
            self.instance and getattr(self.instance, expected_field) is not None
        ):
            raise serializers.ValidationError(
                {
                    expected_field: f"This field is required for data type {attribute.data_type}."
                }
            )

        all_value_fields = ["value_text", "value_number", "value_boolean", "value_date"]
        for field in all_value_fields:
            if field != expected_field:
                attrs[field] = None

        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer used for list views (public list, organizer list)."""

    organizer = serializers.CharField(source="organizer.username", read_only=True)
    seats_left = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "organizer",
            "start_time",
            "end_time",
            "capacity",
            "seats_left",
            "status",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """Full serializer used for retrieve/create/update, includes stages and attributes."""

    organizer = serializers.CharField(source="organizer.username", read_only=True)
    seats_left = serializers.ReadOnlyField()
    stages = EventStageSerializer(many=True, read_only=True)
    attribute_values = EventAttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "start_time",
            "end_time",
            "capacity",
            "seats_left",
            "status",
            "results_published",
            "stages",
            "attribute_values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["organizer", "status", "results_published"]

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )
        return attrs


class EventStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Event.Status.choices)
