from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from raffleshop import views, settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('raffle/<int:identifier>/', views.raffle, name="raffle"),
    path('model/<int:identifier>/', views.series, name="model"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('cart/', views.cart, name="cart"),
    path('checkout/shipping/', views.checkout_shipping, name="checkout_shipping"),
    path('checkout/to_payment/', views.to_payment, name="to_payment"),
    path('checkout/payment/', views.checkout_payment, name="checkout_payment"),
    path('checkout/complete_payment/',
         views.complete_payment, name="complete_payment"),
    path('', views.home, name="home"),
    path('sellers/', views.sellers, name="sellers"),
    path('sellers/dashboard/', views.sellers_dashboard, name="sellers_dashboard"),
    path('create_product/', views.create_product, name="create_product"),
    path('create_raffle_first/', views.create_raffle_first,
         name="create_raffle_first"),
    path('create_raffle_second/', views.create_raffle_second,
         name="create_raffle_second"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
