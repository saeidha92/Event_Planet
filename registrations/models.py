from django.conf import settings
from django.db import models

from events.models import Event


class Registration(models.Model):

    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        unique_together = ("participant", "event")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.participant.username} -> {self.event.title}"
