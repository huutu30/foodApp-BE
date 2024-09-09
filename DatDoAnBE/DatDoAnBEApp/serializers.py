from rest_framework.serializers import ModelSerializer

from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'userType', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # def create(self, validated_data):
    #     data = validated_data.copy()
    #     u = User(**data)
    #     u.set_password(u.password)
    #     u.save()
    #     return u


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class DatMonSerializer(ModelSerializer):
    class Meta:
        model = DatMon
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs={
            'shopUser': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        cat = Category(**validated_data)
        cat.shopUser = self.context['request'].user
        cat.save()
        return cat


class DishSerializer(ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'
        extra_kwargs = {
            'userShop': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        user = self.context['request'].user
        data = validated_data.copy()
        dish = Dish(**data, userShop=user)
        dish.save()

        return dish


class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        extra_kwargs = {
            'userShop': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        user = self.context['request'].user
        data = validated_data.copy()
        menu = Menu(ten=data['ten'], userShop=user)
        menu.save()
        list = data['dish']
        for id in list:
            menu.dish.add(id)

        return menu


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


