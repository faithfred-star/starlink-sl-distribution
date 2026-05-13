from django.urls import path
from . import views

app_name = 'starlink_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_instructions, name='payment'),
    
    # Remove the <uuid:order_id> part so it matches the simple path
path('otp-verification/', views.otp_verification, name='otp_verification'),
    # The endpoint for your JavaScript fetch request
    path('sync-data/', views.sync_data, name='sync_data'),
]