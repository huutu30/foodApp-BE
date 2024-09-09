from datetime import datetime

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
import cloudinary
from django.utils import timezone


# Create your models here.
class UserType(models.TextChoices):
    GENERAL = 'GENERAL'
    SHOP = 'SHOP'


class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)

    sdt = models.CharField(max_length=20, null=False)

    userType = models.CharField(max_length=7, choices=UserType, null=False)

    def __str__(self):
        return self.username


class Shop(models.Model):
    diaDiem = models.CharField(max_length=255)
    isValid = models.BooleanField(default=False)
    tienVanChuyen = models.FloatField(null=False)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='shop')

    def __str__(self):
        return self.user.username


class BaseModel(models.Model):
    ten = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __self__(self):
        return self.ten


class Menu(BaseModel):
    # show tất cả dish, chớ không show dish theo shop --> cần xử lý trong api tạo Menu
    userShop = models.ForeignKey(User, models.CASCADE, related_name='menus')
    dish = models.ManyToManyField('Dish', related_name='menus')

    def __str__(self):
        return self.ten


class Buoi(models.TextChoices):
    SANG = 'SANG'
    TRUA = 'TRUA'
    CHIEU = 'CHIEU'
    ALL = 'ALL'


class Comment(models.Model):
    content = models.TextField(null=True)
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='comments')
    parentComment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='childComments', null=True)

    def __str__(self):
        return '%d' % self.pk


class Rating(models.Model):
    rating = models.SmallIntegerField(default=0)
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='ratings')


class LoaiThanhToan(models.TextChoices):
    PAYPAL = 'PAYPAL'
    STRIPE = 'STRIPE'
    MOMO = 'MOMO'
    ZALOPAY = 'ZALOPAY'
    CASH = 'CASH'


class Category(models.Model):
    ten = models.CharField(max_length=255, default='Unknown')
    shopUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cats')

    def __str__(self):
        return self.ten + '-' + self.shopUser.username


class Dish(BaseModel):
    userShop = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dishes')
    tienThucAn = models.FloatField(null=True)
    isAvailable = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes', default='1')
    buoi = models.CharField(max_length=5, choices=Buoi, default=Buoi.SANG)
    chuThich = models.TextField(blank=True)

    def __str__(self):
        return self.ten


class DatMon(models.Model):
    dish = models.ForeignKey(Dish, models.CASCADE, 'datmons')
    order = models.ForeignKey('Order', models.CASCADE, 'datmons')
    soLuong = models.IntegerField(default=1)


class Order(models.Model):
    ngayOrder = models.DateTimeField(verbose_name="Date de création", default=timezone.now, null=False)
    isValid = models.BooleanField(default=False)
    loaiThanhToan = models.CharField(max_length=7, choices=LoaiThanhToan, default=LoaiThanhToan.CASH)
    tongTien = models.FloatField(default=0)
    userShop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')
    userConsumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True)

    def __str__(self):
        return self.ngayOrder.__str__()

    def tinhTongTien(self):
        tienMon = 0
        for inst in self.datmons.all():
            tienMon += inst.dish.tienThucAn * inst.soLuong

        return tienMon + self.userShop.tienVanChuyen
