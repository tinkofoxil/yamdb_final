from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class AllowPostForAnonymousUser(permissions.BasePermission):
    """Post method permission for anonymous user."""

    def has_permission(self, request, view):
        return request.method == "POST" and request.user.is_anonymous


class AdminUserOnly(permissions.BasePermission):
    """Allow any type of request for authenticated admin user."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AccessPersonalProfileData(permissions.BasePermission):
    """Allow authenticated users to access personal profile."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.username == obj.username


class ReviewCommentPermission(permissions.BasePermission):
    """
    Permission for review and comment models
    Allow:
        READ: for all users
        POST DELETE PATCH: for authenticated owners(authors) of content
        All methods: for authenticated administrators and moderators
    """

    def has_permission(self, request, view):
        user_methods = ["POST", "DELETE", "PATCH"]
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.method in user_methods
            or request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.username == obj.author.username
            or request.user.is_authenticated
            and request.user.is_moderator
        )


class TitleGenreCategoryPermission(permissions.BasePermission):
    """
    Permission for Title,Genre and Category models.
    Allow:
        READ: for all users
        POST DELETE: for authenticated administrators
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )
