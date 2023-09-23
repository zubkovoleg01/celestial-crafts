from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import Product, Category, CartItem, Cart, Order, OrderItem, Favorite, ComparisonItem, Discount
from django.db.models import Q
from django.contrib import messages


def home(request):
    return render(request, 'shop/home.html')


def product(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    selected_categories = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by')

    if selected_categories:
        category_filter = Q(category__in=selected_categories)
        products = products.filter(category_filter)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'price':
        products = products.order_by('price')
    return render(request, 'shop/products.html', {'categories': categories, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'shop/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                Order.objects.create(user=user)
                return redirect('shop:home')
            except IntegrityError:
                return render(request, 'shop/signupuser.html', {'form': UserCreationForm(),
                                                                'error': 'Пользователь с таким именем уже существует!'})
        else:
            return render(request, 'shop/signupuser.html',
                          {'form': UserCreationForm(),
                           'error': 'Пароли не совпали!'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'shop/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'shop/loginuser.html',
                          {'form': AuthenticationForm(),
                           'error': 'Неверные данные для входа!'})
        else:
            login(request, user)
            return redirect('shop:home')

def logoutuser(request):
    logout(request)
    return redirect('shop:home')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, user=request.user)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Так починил корзину для отображения
    cart.items.add(cart_item)
    cart.save()

    return redirect('shop:view_cart')


def delete_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return redirect('shop:view_cart')

def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    new_quantity = request.POST.get('quantity')
    if new_quantity:
        cart_item.quantity = int(new_quantity)
        cart_item.save()
    return redirect('shop:view_cart')

def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    total_price, discount_amount = apply_discount(total_price)

    final_price = total_price - discount_amount
    promo_code_discount = request.session.get('promo_code_discount', 0)
    final_price -= promo_code_discount

    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'discount_amount': discount_amount, 'final_price': final_price, 'promo_code_discount': promo_code_discount})


@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart.items.clear()

    messages.success(request, 'Order placed successfully!')
    return redirect('shop:view_orders')


@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

def favorites(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
        return render(request, 'shop/favorites.html', {'favorites': favorites})
    else:
        return redirect('shop:login')


def add_to_favorite(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        return redirect('shop:products')
    else:
        return redirect('shop:login')


@login_required
def remove_from_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorite, pk=favorite_id)
    favorite.delete()
    return redirect('shop:favorites')


def compare(request):
    if request.user.is_authenticated:
        comparison_items = ComparisonItem.objects.filter(user=request.user)
        return render(request, 'shop/compare.html', {'comparison_items': comparison_items})
    else:
        return redirect('shop:login')


def add_to_comparison(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        comparison, created = ComparisonItem.objects.get_or_create(user=request.user, product=product)
        return redirect('shop:products')
    else:
        return redirect('shop:login')


@login_required
def remove_from_comparison(request, comparison_id):
    comparison = get_object_or_404(ComparisonItem, pk=comparison_id)
    comparison.delete()
    return redirect('shop:compare')

def apply_discount(total_price):
    discount = None
    discount_amount = 0

    if total_price >= 25000:
        discount = Discount.objects.get(name='SALE 8%')
    elif total_price >= 10000:
        discount = Discount.objects.get(name='SALE 5%')

    if discount and discount.is_active():
        discount_amount = total_price * discount.discount_percentage / 100
        total_price -= discount_amount

    return total_price, discount_amount

def apply_promo_code(request):
    promo_code = request.POST.get('promo_code')

    if promo_code == 'NEW500' and not Order.objects.filter(user=request.user).exists():
        discount_amount = request.session.get('promo_code_discount', 0)
        request.session['promo_code_discount'] = max(discount_amount, 500)
        messages.success(request, 'Promo code applied successfully.')
    else:
        messages.error(request, 'Invalid promo code or you already used a promo code.')

    return redirect('shop:view_cart')

def gifts(request):
    return render(request, 'shop/gift.html')