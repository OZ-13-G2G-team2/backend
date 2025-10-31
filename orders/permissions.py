from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', getattr(obj, 'order', None) and obj.order.user) == request.user
