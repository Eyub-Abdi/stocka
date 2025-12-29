from rest_framework import permissions


class IsWholesalerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow wholesalers to edit their products.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the wholesaler who owns the product
        return hasattr(request.user, 'wholesaler_profile') and \
               obj.wholesaler == request.user.wholesaler_profile


class IsShopkeeper(permissions.BasePermission):
    """
    Permission to only allow shopkeepers.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               hasattr(request.user, 'shopkeeper_profile')
