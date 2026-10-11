from django.urls import path

from . import views

# included at /api/participant/
participant_urlpatterns = [
    path("feedback/", views.FeedbackCreateView.as_view(), name="participant-feedback-create"),
]

# included at /api/organizer/
organizer_urlpatterns = [
    path("events/<int:pk>/feedback/", views.EventFeedbackListView.as_view(), name="organizer-event-feedback"),
    path("events/<int:pk>/results/", views.PublishResultsView.as_view(), name="organizer-publish-results"),
]

# included at /api/public/
public_urlpatterns = [
    path("events/<int:pk>/results/", views.PublicResultsView.as_view(), name="public-event-results"),
]
