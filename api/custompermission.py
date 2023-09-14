from rest_framework.permissions import BasePermission



class UserPermision(BasePermission):
    def has_permission(self, request, view):
        user= request.user
        if not user.is_admin and not user.is_doctor:
            return super().has_permission(request, view)
        return False