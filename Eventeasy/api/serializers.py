from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from .models import Category, Service, Order, Cart, CartItem, OrderItem

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'telephone', 'location', 'role')

class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'telephone', 'location', 'role')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()

    class Meta:
        model = Service
        fields = '__all__'

        
class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ('id', 'service', 'quantity', 'total_price')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price')
        
class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'service', 'quantity', 'price', 'total_price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserAccountSerializer()

    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'total_price', 'status', 'created_at', 'updated_at')