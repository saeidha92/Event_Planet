from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOrganizer
from registrations.models import Registration
from registrations.serializers import RegistrationSerializer

from .models import Attribute, Event, EventAttributeValue, EventStage, StageRole
from .permissions import IsEventOwnerOrReadOnlyForOrganizer
from .serializers import (
    AttributeSerializer,
    EventAttributeValueSerializer,
    EventDetailSerializer,
    EventListSerializer,
    EventStageSerializer,
    EventStatusChangeSerializer,
    StageRoleSerializer,
)


# ---------------------------------------------------------------------------
# PUBLIC APIs - no authentication needed
# ---------------------------------------------------------------------------
class PublicEventListView(generics.ListAPIView):
    """GET /api/public/events/  -> only PUBLISHED events are visible to everyone."""

    serializer_class = EventListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.filter(status=Event.Status.PUBLISHED).order_by(
            "start_time"
        )


class PublicEventDetailView(generics.RetrieveAPIView):
    """
    GET /api/public/events/<id>/ -> details of a single event.

    Only DRAFT events are hidden from the public (rule 1 only requires the
    *list* to show PUBLISHED events only). Once an event has been published
    at least once (PUBLISHED / CLOSED / FINISHED) its detail page - and,
    once FINISHED, its results - stay publicly viewable, e.g. so people can
    look back at an event's page and see the published results.
    """

    serializer_class = EventDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.exclude(status=Event.Status.DRAFT)


# ---------------------------------------------------------------------------
# ORGANIZER APIs - only the owning organizer can manage their own events
# ---------------------------------------------------------------------------
class OrganizerEventListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/organizer/events/  -> list only the events owned by the caller
    POST /api/organizer/events/  -> create a new event (status starts as DRAFT)
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        return (
            EventListSerializer
            if self.request.method == "GET"
            else EventDetailSerializer
        )

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user, status=Event.Status.DRAFT)


class OrganizerEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/organizer/events/<id>/ - only the owner."""

    serializer_class = EventDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizer,
        IsEventOwnerOrReadOnlyForOrganizer,
    ]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class EventStatusChangeView(APIView):
    """
    POST /api/organizer/events/<id>/status/
    Body: {"status": "PUBLISHED"}
    Applies the event lifecycle rules (Draft -> Published -> Closed -> Finished).
    """

    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)
        serializer = EventStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        try:
            event.change_status(new_status)
        except DjangoValidationError as exc:
            raise ValidationError({"status": exc.messages})
        return Response(EventDetailSerializer(event).data)


class EventParticipantsView(generics.ListAPIView):
    """GET /api/organizer/events/<id>/participants/ -> registrations for the organizer's own event."""

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event = get_object_or_404(
            Event, pk=self.kwargs["pk"], organizer=self.request.user
        )
        return Registration.objects.filter(event=event).select_related("participant")


# ---------------------------------------------------------------------------
# ORGANIZER APIs - Stages
# ---------------------------------------------------------------------------
class EventStageListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/organizer/events/<id>/stages/ - stages belong to one event."""

    serializer_class = EventStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_event(self):
        return get_object_or_404(
            Event, pk=self.kwargs["pk"], organizer=self.request.user
        )

    def get_queryset(self):
        return EventStage.objects.filter(event=self.get_event())

    def perform_create(self, serializer):

        try:
            serializer.save(event=self.get_event())
        except IntegrityError:
            raise ValidationError(
                {"order": "This event already has a stage with that order number."}
            )


class EventStageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/organizer/stages/<id>/"""

    serializer_class = EventStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return EventStage.objects.filter(event__organizer=self.request.user)


class StageRoleListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/organizer/stages/<id>/roles/ - assign speakers/judges/mentors."""

    serializer_class = StageRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_stage(self):
        return get_object_or_404(
            EventStage, pk=self.kwargs["pk"], event__organizer=self.request.user
        )

    def get_queryset(self):
        return StageRole.objects.filter(stage=self.get_stage())

    def perform_create(self, serializer):
        # unique_together (stage, user, role_type) can be violated -> 400 not 500.
        try:
            serializer.save(stage=self.get_stage())
        except IntegrityError:
            raise ValidationError("This user already has that role on this stage.")


# ---------------------------------------------------------------------------
# ORGANIZER APIs - Dynamic Attributes (EAV)
# ---------------------------------------------------------------------------
class AttributeListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/organizer/attributes/
    Attribute *definitions* are shared metadata: any organizer can reuse an
    attribute already created by someone else (e.g. "platform" for webinars).
    """

    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]


class EventAttributeValueListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/organizer/events/<id>/attribute-values/ - values for ONE event."""

    serializer_class = EventAttributeValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_event(self):
        return get_object_or_404(
            Event, pk=self.kwargs["pk"], organizer=self.request.user
        )

    def get_queryset(self):
        return EventAttributeValue.objects.filter(event=self.get_event())

    def perform_create(self, serializer):

        try:
            serializer.save(event=self.get_event())
        except IntegrityError:
            raise ValidationError(
                {
                    "attribute": "This event already has a value set for that attribute. Use PATCH to update it instead."
                }
            )


class EventAttributeValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PUT/PATCH/DELETE /api/organizer/attribute-values/<id>/"""

    serializer_class = EventAttributeValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return EventAttributeValue.objects.filter(event__organizer=self.request.user)
