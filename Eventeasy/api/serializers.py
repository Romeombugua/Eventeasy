from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from .models import Category, Service, Order, OrderItem
from decimal import Decimal, InvalidOperation

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

        
# class CartItemSerializer(serializers.ModelSerializer):
#     service = ServiceSerializer()
#     total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

#     class Meta:
#         model = CartItem
#         fields = ('id', 'service', 'quantity', 'total_price')

# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True)
#     class Meta:
#         model = Cart
#         fields = ('id', 'items', 'total_price')
        
class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'service', 'quantity', 'price', 'total_price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use user ID reference


    class Meta:
        model = Order
        fields = ('id', 'user', 'items','event_type','paid','mpesa_code', 'total_price','telephone','location','date','status')
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            try:
                # Parse service data
                service_data = item_data.pop('service')
                service, _ = Service.objects.get_or_create(**service_data)

                # Ensure price is a valid decimal
                item_data['price'] = Decimal(item_data['price'])

                # Create the OrderItem
                OrderItem.objects.create(order=order, service=service, **item_data)

            except InvalidOperation:
                raise serializers.ValidationError("Invalid price format.")
            
        return order