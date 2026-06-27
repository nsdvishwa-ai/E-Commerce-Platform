from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('orders/', views.order_history, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('search/', views.search_products, name='search'),
    path('wishlist/<int:product_id>/',views.add_to_wishlist,name='wishlist'),
    path('my-wishlist/', views.wishlist_page, name='wishlist_page'),
    path('buy-now/<int:product_id>/',views.buy_now,name='buy_now'),
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('remove-from-cart/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('increase-quantity/<int:product_id>/',views.increase_quantity,name='increase_quantity'),
]