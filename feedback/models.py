from django.conf import settings
from django.db import models

from events.models import Event


class Feedback(models.Model):

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="feedback_items"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_items",
    )
    rating = models.PositiveSmallIntegerField(
        help_text="Rating from 1 (bad) to 5 (excellent)"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "event",
            "participant",
        )
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback by {self.participant.username} for {self.event.title} ({self.rating}/5)"


class Result(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="results")
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results",
    )
    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        who = self.participant.username if self.participant else "N/A"
        return f"{self.event.title} - {who} - rank {self.rank}"
