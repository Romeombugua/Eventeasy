from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .models import Category, Service, Order, OrderItem
from decimal import Decimal, InvalidOperation

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    # Explicitly declare all fields
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    telephone = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=['CLIENT', 'PROVIDER'], default='CLIENT')

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 
                 'telephone', 'location', 'role')

    def perform_create(self, validated_data):
        print("Performing create with data:", validated_data)  # Debug print
        return super().perform_create(validated_data)

    def create(self, validated_data):
        print("Create method called with data:", validated_data)  # Debug print
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            telephone=validated_data.get('telephone', ''),
            location=validated_data.get('location', ''),
            role=validated_data.get('role', 'CLIENT')
        )
        return user

class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'telephone', 
                 'location', 'role')
        read_only_fields = ('id', 'email')

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
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'service', 'quantity', 'price', 'total_price')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['service'] = ServiceSerializer(instance.service).data
        return representation

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    provider = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'provider', 'items', 'event_type', 'paid', 
                 'mpesa_code', 'taken_by_provider', 'total_price', 'telephone', 
                 'location', 'date', 'status')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            try:
                # The service field now contains just the ID
                service_id = item_data['service'].id
                item_data['price'] = Decimal(item_data['price'])

                OrderItem.objects.create(order=order, service_id=service_id, **item_data)

            except InvalidOperation:
                raise serializers.ValidationError("Invalid price format.")
            
        return order
