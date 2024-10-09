from django.contrib import admin
from .models import Category, Service, Order, UserAccount, OrderItem

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

# Service Admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')
    list_per_page = 25

# OrderItem Inline (to view in the Order page)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'status')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    list_per_page = 25

# UserAccount Admin
@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'telephone', 'location', 'role')
    list_per_page = 25

# CartItem Inline (to view in the Cart page)
# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 1

# # Cart Admin
# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'created_at')
#     inlines = [CartItemInline]
#     ordering = ('-created_at',)
#     list_per_page = 25

# # CartItem Admin
# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'cart', 'service', 'quantity')
#     list_per_page = 25

# OrderItem Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'service', 'quantity')
    list_per_page = 25
