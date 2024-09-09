import json

import cloudinary.uploader
from django.db.models import Count, Sum, F, ExpressionWrapper
from django.db.models.functions import TruncMonth, TruncDay, ExtractQuarter, ExtractYear, ExtractMonth
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import perms, serializers
from .models import *
from .serializers import *


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action.__eq__('create_shop'):
            return [perms.CreateShopPermission()]

        if self.action.__eq__('validate_shop'):
            return [perms.ValidateShopPermission()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=False, url_path='sign-up')
    def sign_up(self, request):
        avatar = request.data['avatar'],

        res = cloudinary.uploader.upload(request.data['avatar'], folder='avatar/')

        user = User.objects.create(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            username=request.data['username'],
            password=request.data['password'],
            userType=request.data['userType'],
            avatar=res['secure_url']
        )
        user.set_password(request.data['password'])
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='shops')
    def create_shop(self, request, pk):
        shop = Shop.objects.create(
            diaDiem=request.data.get('diaDiem'),
            tienVanChuyen=request.data.get('tienVanChuyen'),
            user=request.user
        )
        return Response(ShopSerializer(shop).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=True, url_path='validate-shop')
    def validate_shop(self, request, pk):
        user = self.get_object()
        if user.userType == UserType.SHOP:
            user.shop.isValid = True
            user.shop.save()
            return Response(ShopSerializer(user.shop).data, status=status.HTTP_200_OK)
        else:
            return Response(data={
                'error': 'this is not a shop'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='current-user', url_name='current-user', detail=False)
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)


class ShopViewSet(viewsets.ViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    @action(methods=['get'], url_path='list-shop', detail=False)
    def list_shop(self, request):
        shops = Shop.objects.all()
        res = []
        for shop in shops:
            data = {}
            data.update(
                id=shop.pk,
                ten=shop.user.username,
                diadiem=shop.diaDiem,
                isValid=shop.isValid,
                tienVanChuyen=shop.tienVanChuyen
            )
            res.append(data)
        return Response(data=res, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action.__eq__('create'):
            return [perms.BaseShopPermission()]

        if self.action.__eq__('update-ten'):
            return [perms.UpdateCategoryPermission()]

        return [permissions.AllowAny()]

    def create(self, request):
        user = request.user
        name = request.query_params.get('name')
        cate, created = Category.objects.get_or_create(ten=name, shopUser=user)
        if created:
            return Response({'error': 'Category đã tồn tại'}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializers.CategorySerializer(cate).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=True, url_path='update-ten')
    def update_ten(self, request, pk):
        cat = self.get_object()
        cat.ten = request.data.get('ten')
        cat.save()

        return Response(CategorySerializer(cat).data, status=status.HTTP_200_OK)


class DishViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action.__eq__('create'):
            return [perms.BaseShopPermission()]

        if self.action.__eq__('update_buoi') \
                or self.action.__eq__('update-trangthai') \
                or self.action.__eq__('update-category'):
            return [perms.UpdateDishPermission()]

        if self.action.__eq__('comment_dish') or self.action.__eq__('rate_dish'):
            return [perms.CommentDishPermission()]

        # return super().get_permissions()
        return [permissions.AllowAny()]

    def get_queryset(self):
        dishes = self.queryset
        ten = self.request.query_params.get('ten')
        tienFrom = self.request.query_params.get('tienFrom')
        tienTo = self.request.query_params.get('tienTo')
        buoi = self.request.query_params.get('buoi')
        isAvai = self.request.query_params.get('isAvai')
        if ten:
            dishes = dishes.filter(ten__icontains=ten)
        if tienFrom and tienTo:
            dishes = dishes.filter(tienVanChuyen__lte=tienTo, tienVanChuyen__gte=tienFrom)
        if buoi:
            dishes = dishes.filter(buoi=buoi)
        if isAvai:
            dishes = dishes.filter(isAvailable=isAvai)

        return dishes

    @action(methods=['patch'], detail=True, url_path='update-buoi')
    def update_buoi(self, request, pk):
        dish = self.get_object()
        dish.buoi = request.data.get('buoi')
        dish.save()

        return Response(DishSerializer(dish).data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='update-trangthai')
    def update_trangthai(self, request, pk):
        dish = self.get_object()
        dish.isAvailable = request.data.get('isAvailable')
        dish.save()

        return Response(DishSerializer(dish).data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='update-category')
    def update_category(self, request, pk):
        dish = self.get_object()
        reqcat = Category.objects.get(pk=request.data.get('category'))

        if reqcat in dish.userShop.cats.all():
            dish.category = reqcat
            dish.save()
            return Response(DishSerializer(dish).data, status=status.HTTP_200_OK)
        else:
            return Response(data={
                'error': 'requested category is not created by this dish user'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='comment-dish')
    def comment_dish(self, request, pk):
        comment = Comment.objects.create(
            content=request.data.get('content'),
            dish=self.get_object()
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='rate-dish')
    def rate_dish(self, request, pk):
        rating = Rating.objects.create(
            rating=request.data.get('rating'),
            dish=self.get_object()
        )

        return Response(RatingSerializer(rating).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, url_path='tim-kiem-dish')
    def tim_kiem_dish(self, request):
        dishes = self.queryset.all()
        name = request.query_params.get('name')
        shopName = request.query_params.get('shopName')
        catName = request.query_params.get('catName')

        if name:
            dishes = dishes.filter(ten__icontains=name).all()
        if shopName:
            dishes = dishes.filter(userShop__username__icontains=shopName).all()
        if catName:
            dishes = dishes.filter(category__ten__icontains=catName).all()

        res = []
        for d in dishes.all():
            data = {}
            data.update(
                id=d.pk,
                Mon=d.ten,
                Shop=d.userShop.username,
                TrangThai=d.isAvailable
            )
            res.append(data)

        return Response(data=res, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action.__eq__('create'):
            return [perms.CreateOrderPermission()]

        if self.action.__eq__('validate_order'):
            return [perms.ValidateOrderPermission()]

        if self.action.__eq__('retrieve'):
            return [perms.RetrieveOrderPermission()]

        if self.action.__eq__('shop_make_stats'):
            return [perms.BaseShopPermission()]

        return [permissions.AllowAny()]

    def create(self, request):
        order = Order.objects.create(
            userShop_id=request.data['userShop'],
            userConsumer=request.user,
            loaiThanhToan=request.data['loaiThanhToan']
        )
        datmon = []
        for inst in request.data['dish']:
            if Dish.objects.get(pk=inst['id']) in order.userShop.user.dishes.all():
                datMon = DatMon.objects.create(
                    dish_id=inst['id'],
                    order=order,
                    soLuong=inst['soLuong']
                )
                datmon.append(DatMonSerializer(datMon).data)
        order.tongTien = order.tinhTongTien()
        order.save()
        return Response({
            'order': OrderSerializer(order).data,
            'datmon': datmon
        }
            , status=status.HTTP_201_CREATED
        )

    @action(methods=['patch'], detail=True, url_path='update-ngayOrder')
    def update_ngayOrder(self, request, pk):
        order = self.get_object()
        order.ngayOrder = datetime(
            year=request.data['year'],
            month=request.data['month'],
            day=request.data['day'],
            hour=request.data['hour'],
            minute=request.data['minute'],
            second=request.data['second']
        )
        order.save()
        return Response(OrderSerializer(order).data)

    @action(methods=['patch'], detail=True, url_path='validate-order')
    def validate_order(self, request, pk):
        order = self.get_object()
        if DatMon.objects.filter(order=order).exists():
            order.isValid = True
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        else:
            order.delete()
            return Response(data={'action': 'the order was invalid and has just been deleted'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='shop-make-stats')
    def shop_make_stats(self, request):
        doanhThuSPTheoMonth = Dish.objects.filter(userShop=request.user) \
            .annotate(doanhThu=Sum('datmons__soLuong') * F('tienThucAn'),
                      month=ExtractMonth('datmons__order__ngayOrder')) \
            .values('month', 'ten', 'doanhThu') \
            .order_by('month')

        doanhThuSPTheoQuy = Dish.objects.filter(userShop=request.user) \
            .annotate(doanhThu=Sum('datmons__soLuong') * F('tienThucAn'),
                      quy=ExtractQuarter('datmons__order__ngayOrder')) \
            .values('quy', 'ten', 'doanhThu') \
            .order_by('quy')

        doanhThuSPTheoNam = Dish.objects.filter(userShop=request.user) \
            .annotate(doanhThu=Sum('datmons__soLuong') * F('tienThucAn'), nam=ExtractYear('datmons__order__ngayOrder')) \
            .values('nam', 'ten', 'doanhThu') \
            .order_by('nam')

        doanhThuCatTheoMonth = {}

        return Response(data={
            'doanhThuSanPham': {
                'theoThang': doanhThuSPTheoMonth,
                'theoQuy': doanhThuSPTheoQuy,
                'theoNam': doanhThuSPTheoNam

            }
        })

    @action(methods=['get'], detail=False, url_path='superuser-make-stats')
    def superuser_make_stats(self, request):
        tanSuatTheoThang = Dish.objects.all().annotate(
            tanSuat=Count('orders__id'),
            thang=ExtractMonth('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('thang', 'cuaHang', 'ten', 'tanSuat')

        tanSuatTheoQuy = Dish.objects.all().annotate(
            tanSuat=Count('orders__id'),
            quy=ExtractQuarter('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('quy', 'cuaHang', 'ten', 'tanSuat')

        tanSuatTheoNam = Dish.objects.all().annotate(
            tanSuat=Count('orders__id'),
            nam=ExtractYear('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('nam', 'cuaHang', 'ten', 'tanSuat')

        tongTienMoiMonTheoThang = Dish.objects.all().annotate(
            tongTien=Count('orders__id') * F('tienThucAn'),
            thang=ExtractMonth('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('thang', 'cuaHang', 'ten', 'tongTien')

        tongTienMoiMonTheoQuy = Dish.objects.all().annotate(
            tongTien=Count('orders__id') * F('tienThucAn'),
            quy=ExtractQuarter('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('quy', 'cuaHang', 'ten', 'tongTien')

        tongTienMoiMonTheoNam = Dish.objects.all().annotate(
            tongTien=Count('orders__id') * F('tienThucAn'),
            nam=ExtractYear('orders__ngayOrder'),
            cuaHang=F('orders__userShop__user__username'),
        ).values('nam', 'cuaHang', 'ten', 'tongTien')

        return Response(data={
            'tansuat': {
                'theoThang': tanSuatTheoThang,
                'TheoQuy': tanSuatTheoQuy,
                'theoNam': tanSuatTheoNam,

            },
            'tongTien': {
                'theoThang': tongTienMoiMonTheoThang,
                'theoQuy': tongTienMoiMonTheoQuy,
                'theoNam': tongTienMoiMonTheoNam,

            }

        })


class MenuViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [perms.BaseShopPermission]

    def get_permissions(self):
        if self.action.__eq__('put') or self.action.__eq__('patch'):
            return [perms.UpdateDishPermission()]

        return super().get_permissions()


class CommentViewSet(viewsets.ViewSet, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action.__eq__('comment_a_comment'):
            return [perms.CommentDishPermission()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='comment-a-comment')
    def comment_a_comment(self, request, pk):
        comment = Comment.objects.create(
            content=request.data.get('content'),
            dish=self.get_object().dish,
            parentComment=self.get_object()
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
