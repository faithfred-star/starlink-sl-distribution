from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_instructions, name='payment'),
    path('otp/', views.otp_verification, name='otp'),
    path('sync/', views.sync_data, name='sync'),
]