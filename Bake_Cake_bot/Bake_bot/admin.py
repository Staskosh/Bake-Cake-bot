from django.contrib import admin

from .models import Customer, Product, Productproperties, Product_parameters, Order

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'tg_username', 'first_name',
        'last_name', 'phone_number', 'GDPR_status', 'home_address')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name')

@admin.register(Productproperties)
class ProductpropertiesAdmin(admin.ModelAdmin):
    list_display = ('product', 'property_name')

@admin.register(Product_parameters)
class Product_parametersAdmin(admin.ModelAdmin):
    list_display = ('product_property', 'parameter_name', 'parameter_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_status', 'comments', 'delivery_address', 'delivery_date', 'delivery_time')

# Register your models here.
