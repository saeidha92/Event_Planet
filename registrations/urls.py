from django.urls import path

from . import views

# included at /api/participant/
participant_urlpatterns = [
    path(
        "registrations/",
        views.RegistrationListCreateView.as_view(),
        name="participant-registration-list",
    ),
]
