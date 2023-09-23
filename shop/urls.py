from django.urls import path
from . import views


app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('signup/', views.signupuser, name='signup'),
    path('logout/', views.logoutuser, name='logout'),
    path('login/', views.loginuser, name='login'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_from_cart/<int:cart_item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('update_cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    path('orders/', views.view_orders, name='view_orders'),
    path('create_order/', views.create_order, name='create_order'),
    path('favorites/', views.favorites, name='favorites'),
    path('add_to_favorite/<int:product_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('remove_from_favorite/<int:favorite_id>/', views.remove_from_favorite, name='remove_from_favorite'),
    path('compare/', views.compare, name='compare'),
    path('add_to_comparison/<int:product_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('remove_from_comparison/<int:comparison_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('apply_promo_code/', views.apply_promo_code, name='apply_promo_code'),
    path('gift/', views.gifts, name='gifts'),
]

