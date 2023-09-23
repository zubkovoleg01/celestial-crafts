from django.contrib import admin
from .models import Product, Category, Cart, CartItem, Order, Discount

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'image']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Discount)
