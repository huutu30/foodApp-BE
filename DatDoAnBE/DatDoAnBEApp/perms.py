from rest_framework import permissions

from .models import UserType


class CreateShopPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.userType == UserType.SHOP


class ValidateShopPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser == True


class BaseShopPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) \
            and request.user.userType == UserType.SHOP \
            and request.user.shop.isValid == True


class CreateOrderPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.userType == UserType.GENERAL


class BaseOrderPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user.pk == obj.userShop.pk


class ValidateOrderPermission(BaseOrderPermission):
    pass


class RetrieveOrderPermission(BaseOrderPermission):
    def has_object_permission(self, request, view, obj):
        return (self.has_permission(request, view) and request.user == obj.userConsumer) \
            or super().has_object_permission(request, view, obj)


class UpdateDishPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj.userShop


class CommentDishPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.userType == UserType.GENERAL


class UpdateCategoryPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj.shopUser
