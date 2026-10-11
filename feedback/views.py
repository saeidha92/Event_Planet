from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOrganizer, IsParticipant
from events.models import Event

from .models import Feedback, Result
from .serializers import FeedbackSerializer, ResultSerializer


# ---------------------------------------------------------------------------
# PARTICIPANT APIs
# ---------------------------------------------------------------------------
class FeedbackCreateView(generics.CreateAPIView):

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def perform_create(self, serializer):

        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError("You already submitted feedback for this event.")


# ---------------------------------------------------------------------------
# ORGANIZER APIs
# ---------------------------------------------------------------------------
class EventFeedbackListView(generics.ListAPIView):

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["pk"], organizer=self.request.user)
        return Feedback.objects.filter(event=event)


class PublishResultsView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)

        if event.status != Event.Status.FINISHED:
            raise ValidationError("Results can only be published after the event is FINISHED.")

        results_data = request.data.get("results", [])
        if not isinstance(results_data, list) or not results_data:
            raise ValidationError({"results": "Provide a non-empty list of result rows."})

        event.results.all().delete()
        created = []
        for row in results_data:
            serializer = ResultSerializer(data=row)
            serializer.is_valid(raise_exception=True)
            created.append(serializer.save(event=event))

        event.results_published = True
        event.save(update_fields=["results_published"])

        return Response(ResultSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# PUBLIC APIs
# ---------------------------------------------------------------------------
class PublicResultsView(generics.ListAPIView):


    serializer_class = ResultSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        if not event.results_published:
            return Result.objects.none()
        return Result.objects.filter(event=event)

