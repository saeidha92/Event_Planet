from django.db import IntegrityError
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from accounts.permissions import IsParticipant

from .models import Registration
from .serializers import RegistrationSerializer


class RegistrationListCreateView(generics.ListCreateAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Registration.objects.filter(participant=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError("You are already registered for this event.")
