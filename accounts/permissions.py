from rest_framework.permissions import BasePermission, SAFE_METHODS

class RolePermission(BasePermission):
    """Base class for role-based API access control."""
    allowed_roles = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and
                    (user.is_superuser or user.role in self.allowed_roles))

class IsAdmin(RolePermission):
    allowed_roles = ("ADMIN",)

class IsAgent(RolePermission):
    allowed_roles = ("AGENT",)

class IsCustomer(RolePermission):
    allowed_roles = ("CUSTOMER",)

class IsAdminOrAgent(RolePermission):
    allowed_roles = ("ADMIN", "AGENT")

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated)
        return bool(user and user.is_authenticated and
                    (user.is_superuser or user.role == "ADMIN"))

class IsOwnerOrAdmin(BasePermission):
    """Object-level check for common ownership relations."""
    owner_fields = ("user", "customer", "created_by")

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.role == "ADMIN":
            return True
        for field in self.owner_fields:
            owner = getattr(obj, field, None)
            if owner is not None:
                return owner == user
        return False
