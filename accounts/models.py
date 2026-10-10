from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.
    We add a 'role' field so every user is either a Participant or an Organizer.
    A simple CharField with choices is enough here (roles do not change
    dynamically, so we do not need a separate Role table).
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
