from django.urls import path
from . import views

app_name = 'starlink_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_instructions, name='payment'),
    
    # Corrected UUID path to match your views
    path('otp/<uuid:order_id>/', views.otp_verification, name='otp_verification'),
    
    # The endpoint for your JavaScript fetch request
    path('sync-data/', views.sync_data, name='sync_data'),
]