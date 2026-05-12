from django.urls import path
from . import views

# This app_name must match the namespace used in your main starlink_config/urls.py
app_name = 'starlink_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('', include('starlink_app.urls', namespace='starlink_app')
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_instructions, name='payment'),
    
    # CORRECTED: Added <uuid:order_id> to prevent 404 and allow the view to find the order
    path('otp/<uuid:order_id>/', views.otp_verification, name='otp_verification'),
    
    # The endpoint for your JavaScript fetch request
    path('sync-data/', views.sync_data, name='sync_data'),
]