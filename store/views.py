from django.shortcuts import render, get_object_or_404
from .models import Product, Cart
from .models import Product, Category, Cart
from django.db.models import Sum

def home(request):

    categories = Category.objects.all()

    products = Product.objects.all()

    category_id = request.GET.get('category')
    sort = request.GET.get('sort')

    if category_id:
        products = products.filter(category_id=category_id)
    if sort == "low":
            products = products.order_by('price')

    elif sort == "high":
            products = products.order_by('-price')

    elif sort == "az":
            products = products.order_by('name')

    elif sort == "za":
            products = products.order_by('-name')

    

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

from django.contrib import messages

@login_required
def add_to_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    # Check stock
    if product.stock <= 0:
        messages.error(request, "Sorry! This product is out of stock.")
        return redirect('product_detail', product_id=product.id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        # Don't allow more than available stock
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, "Maximum available stock already added.")

    return redirect('cart')

@login_required
def cart(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        item.total_price = item.product.price * item.quantity
        total += item.total_price

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

from decimal import Decimal
from .models import Product, Cart, Order, OrderItem
@login_required
@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    return redirect('payment')
def order_success(request):
    return render(request, 'store/order_success.html')

from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'store/order_detail.html', {
        'order': order,
        'items': items
    })

from django.http import JsonResponse

def search_products(request):

    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    data = []

    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else ""
        })

    return JsonResponse(data, safe=False)

from django.shortcuts import redirect
from .models import Product, Wishlist
@login_required
def add_to_wishlist(request, product_id):

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('home')

from .models import Wishlist

def wishlist_page(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'items': items})

from decimal import Decimal
from django.contrib import messages

@login_required
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect('product_detail', product_id=product.id)

    # Save product id in session
    request.session['buy_now_product'] = product.id

    return redirect('payment')

from decimal import Decimal
@login_required
def payment(request):

    if 'buy_now_product' in request.session:

        product = Product.objects.get(
            id=request.session['buy_now_product']
        )

        total = product.price

    else:

        cart_items = Cart.objects.filter(user=request.user)

        total = Decimal("0.00")

        for item in cart_items:
            total += item.product.price * item.quantity

    return render(request, 'store/payment.html', {
        'total': total
    })

@login_required
def payment_success(request):

    # ---------- Buy Now ----------
    if 'buy_now_product' in request.session:

        product = Product.objects.get(
            id=request.session['buy_now_product']
        )

        order = Order.objects.create(
            user=request.user,
            total_amount=product.price
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )

        product.stock -= 1
        product.save()

        del request.session['buy_now_product']

        return redirect('order_success')

    # ---------- Cart Checkout ----------
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    total = Decimal("0.00")

    for item in cart_items:
        total += item.product.price * item.quantity

    order = Order.objects.create(
        user=request.user,
        total_amount=total
    )

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        item.product.stock -= item.quantity
        item.product.save()

    cart_items.delete()

    return redirect('order_success')


@login_required
def remove_from_cart(request, product_id):

    cart_item = Cart.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.delete()

    return redirect('cart')

@login_required
def increase_quantity(request, product_id):

    cart_item = Cart.objects.get(
        user=request.user,
        product_id=product_id
    )

    # Check stock before increasing quantity
    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')