from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):


    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        if hasattr(obj, "user"):
            return obj.user == request.user


        if hasattr(obj, "order") and hasattr(obj.order, "user"):
            return obj.order.user == request.user


        return False
