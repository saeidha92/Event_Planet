from rest_framework.permissions import BasePermission


class IsParticipant(BasePermission):
    """Allows access only to users with the PARTICIPANT role."""

    message = "Only participants can access this API."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_participant()
        )


class IsOrganizer(BasePermission):
    """Allows access only to users with the ORGANIZER role."""

    message = "Only organizers can access this API."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_organizer()
        )


class IsEventOwner(BasePermission):
    """
    Object level permission: only the organizer who owns the event
    (obj.organizer) is allowed to edit/manage it.
    """

    message = "You can only manage events that you own."

    def has_object_permission(self, request, view, obj):

        event = obj if hasattr(obj, "organizer") else getattr(obj, "event", None)
        return bool(event and event.organizer_id == request.user.id)
