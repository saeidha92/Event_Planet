from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsEventOwnerOrReadOnlyForOrganizer(BasePermission):

    def has_object_permission(self, request, view, obj):
        event = obj if hasattr(obj, "organizer") else obj.event
        return event.organizer_id == request.user.id
