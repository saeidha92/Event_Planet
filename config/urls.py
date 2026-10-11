"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from events.urls import organizer_urlpatterns as events_organizer_urls
from events.urls import public_urlpatterns as events_public_urls
from feedback.urls import organizer_urlpatterns as feedback_organizer_urls
from feedback.urls import participant_urlpatterns as feedback_participant_urls
from feedback.urls import public_urlpatterns as feedback_public_urls
from registrations.urls import participant_urlpatterns as registrations_participant_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/public/", include(events_public_urls + feedback_public_urls)),
    path(
        "api/participant/",
        include(registrations_participant_urls + feedback_participant_urls),
    ),
    path("api/organizer/", include(events_organizer_urls + feedback_organizer_urls)),
]
