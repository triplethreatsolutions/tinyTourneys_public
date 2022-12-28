# Core Django imports
from django.db.models import Q
from django.contrib.auth import get_user_model

# 3rd party imports
from rest_framework.permissions import BasePermission, SAFE_METHODS

# app imports
from .models import Organization

User = get_user_model()


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CanViewOrgs(BasePermission):
    """
    Custom permission to only allow users to view organizations.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method in SAFE_METHODS and bool(request.user):
            return True

        return False


class CanEditOrg(BasePermission):
    """
    Custom permission to only allow users of an object to view and edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        found = (obj.admin_id == request.user.id) | obj.directors.filter(
            id=request.user.id
        ).exists()
        user = User.objects.get(pk=request.user.id)
        if bool(
            request.user and found and user.has_perm("users.can_edit_organization")
        ):
            return True

        return False
