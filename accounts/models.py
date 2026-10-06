from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model that extends the default Django AbstractUser.
    Additional fields can be added here if needed.
    """

    class Role(models.TextChoices):
        PARTICIPANT = "PARTICIPANT", "Participant"
        ORGANIZER = "ORGANIZER", "Organizer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT,
        help_text="Role of the user: PARTICIPANT or ORGANIZER",
    )

    def is_participant(self):
        return self.role == self.Role.PARTICIPANT

    def is_organizer(self):
        return self.role == self.Role.ORGANIZER

    def __str__(self):
        return f"{self.username} ({self.role})"
