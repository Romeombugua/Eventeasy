from rest_framework import viewsets, permissions, status
from .models import Category, Service, Order, UserAccount, OrderItem
from .serializers import CategorySerializer, ServiceSerializer, OrderSerializer, UserCreateSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        print("Valid data received:", serializer.validated_data)  # Debug print
        user = serializer.save()
        return Response({
            'user': UserCreateSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    print("Validation errors:", serializer.errors)  # Debug print
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserAccount.objects.all()
        return UserAccount.objects.filter(id=self.request.user.id)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # def perform_create(self, serializer):
    #     serializer.save(provider=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return Order.objects.filter(user=user)
        elif user.role == 'PROVIDER':
            # Providers can see unclaimed orders and their own claimed orders
            return Order.objects.filter(
                Q(provider__isnull=True) |  # Unclaimed orders
                Q(provider=user)  # Orders claimed by this provider
            )
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def claim_order(self, request, pk=None):
        order = self.get_object()
        user = request.user

        # Check if user is a provider
        if user.role != 'PROVIDER':
            return Response(
                {"error": "Only providers can claim orders"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if order is already claimed
        if order.provider is not None:
            return Response(
                {"error": "This order has already been claimed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if order is in PENDING status
        if order.status != 'PENDING':
            return Response(
                {"error": "Only pending orders can be claimed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Claim the order
        order.provider = user
        order.taken_by_provider = True
        order.status = 'PROCESSING'
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def release_order(self, request, pk=None):
        order = self.get_object()
        user = request.user

        # Check if this provider owns the order
        if order.provider != user:
            return Response(
                {"error": "You can only release orders you have claimed"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Release the order
        order.provider = None
        order.taken_by_provider = False
        order.status = 'PENDING'
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)
    


        
# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.none()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     @action(detail=True, methods=['post'])
#     def add_to_cart(self, request, pk=None):
#         cart = self.get_object()
#         service_id = request.data.get('service')
#         quantity = int(request.data.get('quantity', 1))

#         service = get_object_or_404(Service, id=service_id)
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             service=service,
#             defaults={'quantity': quantity}
#         )

#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)

#     @action(detail=True, methods=['post'])
#     def remove_from_cart(self, request, pk=None):
#         cart = self.get_object()
#         cart_item_id = request.data.get('cart_item_id')

#         cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
#         cart_item.delete()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)

#     @action(detail=True, methods=['post'])
#     def checkout(self, request, pk=None):
#         cart = self.get_object()
        
#         if not cart.items.exists():
#             return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

#         order = Order.objects.create(
#             user=request.user,
#             total_price=cart.total_price
#         )

#         for cart_item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 service=cart_item.service,
#                 quantity=cart_item.quantity,
#                 price=cart_item.service.price
#             )

#         cart.items.all().delete()

#         order_serializer = OrderSerializer(order)
#         return Response(order_serializer.data, status=status.HTTP_201_CREATED)

