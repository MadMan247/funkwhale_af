import operator

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.permissions import BasePermission

from funkwhale_api.common import preferences


class ConditionalAuthentication(BasePermission):
    def has_permission(self, request, view):
        if preferences.get("common__api_authentication_required"):
            return (request.user and request.user.is_authenticated) or (
                hasattr(request, "actor") and request.actor
            )
        return True


class OwnerPermission(BasePermission):
    """
    Ensure the request user is the owner of the object.

    Usage:

    class MyView(APIView):
        model = MyModel
        permission_classes = [OwnerPermission]
        owner_field = 'owner'
        owner_checks = ['read', 'write']
    """

    perms_map = {
        "GET": "read",
        "OPTIONS": "read",
        "HEAD": "read",
        "POST": "write",
        "PUT": "write",
        "PATCH": "write",
        "DELETE": "write",
    }

    def has_object_permission(self, request, view, obj):
        method_check = self.perms_map[request.method]
        owner_checks = getattr(view, "owner_checks", ["read", "write"])
        if method_check not in owner_checks:
            # check not enabled
            return True

        owner_field = getattr(view, "owner_field", "user")
        owner_exception = getattr(view, "owner_exception", Http404)
        try:
            owner = operator.attrgetter(owner_field)(obj)
        except ObjectDoesNotExist:
            raise owner_exception

        if not owner or not request.user.is_authenticated or owner != request.user:
            raise owner_exception
        return True


class PrivacyLevelPermission(BasePermission):
    """
    Ensure the request actor have access to the object considering the privacylevel configuration
    of the user.
    request.user is None if actor, else its Anonymous if user is not auth.
    """

    def has_object_permission(self, request, view, obj):
        if (
            not hasattr(obj, "user")
            and hasattr(obj, "actor")
            and not obj.actor.is_local
        ):
            # it's a remote actor object. It should be public.
            # But we could trigger an update of the remote actor data
            # to avoid leaking data (#2326)
            return True

        if hasattr(obj, "privacy_level"):
            privacy_level = obj.privacy_level
        elif hasattr(obj, "actor") and obj.actor.user:
            privacy_level = obj.actor.user.privacy_level
        else:
            privacy_level = obj.user.privacy_level

        obj_actor = obj.actor if hasattr(obj, "actor") else obj.user.actor

        if privacy_level == "everyone":
            return True

        # user is anonymous
        if hasattr(request, "actor"):
            request_actor = request.actor
        elif request.user and request.user.is_authenticated:
            request_actor = request.user.actor
        else:
            return False

        if privacy_level == "instance":
            # user is local
            if request.user and hasattr(request.user, "actor"):
                return True
            elif hasattr(request, "actor") and request.actor and request.actor.is_local:
                return True
            else:
                return False

        elif privacy_level == "me" and obj_actor == request_actor:
            return True

        elif request_actor in obj_actor.get_approved_followers():
            return True
        else:
            return False
