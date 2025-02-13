from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAdminOrAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in SAFE_METHODS)
