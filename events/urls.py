from django.urls import path

from . import views

# Public endpoints -> included at /api/public/
public_urlpatterns = [
    path("events/", views.PublicEventListView.as_view(), name="public-event-list"),
    path(
        "events/<int:pk>/",
        views.PublicEventDetailView.as_view(),
        name="public-event-detail",
    ),
]

# Organizer endpoints -> included at /api/organizer/
organizer_urlpatterns = [
    path(
        "events/",
        views.OrganizerEventListCreateView.as_view(),
        name="organizer-event-list",
    ),
    path(
        "events/<int:pk>/",
        views.OrganizerEventDetailView.as_view(),
        name="organizer-event-detail",
    ),
    path(
        "events/<int:pk>/status/",
        views.EventStatusChangeView.as_view(),
        name="organizer-event-status",
    ),
    path(
        "events/<int:pk>/participants/",
        views.EventParticipantsView.as_view(),
        name="organizer-event-participants",
    ),
    path(
        "events/<int:pk>/stages/",
        views.EventStageListCreateView.as_view(),
        name="organizer-stage-list",
    ),
    path(
        "stages/<int:pk>/",
        views.EventStageDetailView.as_view(),
        name="organizer-stage-detail",
    ),
    path(
        "stages/<int:pk>/roles/",
        views.StageRoleListCreateView.as_view(),
        name="organizer-stage-roles",
    ),
    path(
        "attributes/",
        views.AttributeListCreateView.as_view(),
        name="organizer-attribute-list",
    ),
    path(
        "events/<int:pk>/attribute-values/",
        views.EventAttributeValueListCreateView.as_view(),
        name="organizer-event-attribute-values",
    ),
    path(
        "attribute-values/<int:pk>/",
        views.EventAttributeValueDetailView.as_view(),
        name="organizer-attribute-value-detail",
    ),
]
