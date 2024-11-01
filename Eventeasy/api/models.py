from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Additional fields from UserProfile
    telephone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('CLIENT', 'Client'),
        ('PROVIDER', 'Provider'),
    ], default='CLIENT')

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    

    def __str__(self):
        return self.name

# class Cart(models.Model):
#     user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='cart')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Cart for {self.user.email}"

#     @property
#     def total_price(self):
#         return sum(item.total_price for item in self.items.all())

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return f"{self.quantity} x {self.service.name} in cart for {self.cart.user.email}"

#     @property
#     def total_price(self):
#         return self.service.price * self.quantity

# class Order(models.Model):
#     ORDER_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('PROCESSING', 'Processing'),
#         ('COMPLETED', 'Completed'),
#         ('CANCELLED', 'Cancelled'),
#     ]

#     user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='orders')
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
#     location = models.CharField(max_length=100, default='Nairobi')
#     telephone = models.CharField(max_length=15, default='0712345678')
#     date = models.DateField(default='2022-01-01')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Order {self.id} by {self.user.email}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

#     def __str__(self):
#         return f"{self.quantity} x {self.service.name} in order {self.order.id}"

#     @property
#     def total_price(self):
#         return self.price * self.quantity

# class Service(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     category = models.IntegerField()

#     def __str__(self):
#         return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    event_type = models.CharField(max_length=100, default="Others")
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    mpesa_code = models.CharField(max_length=10, blank=True)
    taken_by_provider = models.BooleanField(default=False)
    telephone = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.service.name} for Order {self.order.id}"
