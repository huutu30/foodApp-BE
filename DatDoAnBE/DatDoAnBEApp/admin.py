from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission, ContentType, Group


class DishAdmin(admin.ModelAdmin):
    list_display = ['pk', 'ten', 'userShop', 'category', 'tienThucAn', 'isAvailable', 'buoi', 'chuThich']


class MenuAdmin(admin.ModelAdmin):
    list_display = ['pk', 'ten', 'userShop']


class ShopAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user']


class UserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'ngayOrder', 'userShop', 'userConsumer']
    readonly_fields = ['ngayOrder']


class DatMonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'dish', 'order_id', 'soLuong']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'dish', 'parentComment']


class RatingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'rating', 'dish']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'ten', 'shopUser']


# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(DatMon, DatMonAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Permission)
admin.site.register(ContentType)
