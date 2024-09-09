from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('dishes', DishViewSet, basename='dishes')
router.register('menus', MenuViewSet, basename='menus')
router.register('orders', OrderViewSet, basename='orders')
router.register('comments', CommentViewSet, basename='comments')
router.register('categories', CategoryViewSet, basename='categories')
router.register('shops', ShopViewSet, basename='shops')

urlpatterns = [
    path('', include(router.urls))
]
