from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class Bundle(models.Model):
    """Starlink bundle packages specifically for the Sierra Leone market"""
    BUNDLE_TYPES = [
        ('FREE', 'Experience Pass'),
        ('LITE', 'Lite Pass'),
        ('SOCIAL', 'Social Plus'),
        ('POWER', 'Power User'),
        ('STREAMER', 'Streamer'),
        ('ELITE', 'Elite Pass'),
    ]

    name = models.CharField(max_length=100)
    bundle_type = models.CharField(max_length=20, choices=BUNDLE_TYPES)
    description = models.TextField()
    data_gb = models.CharField(max_length=50)
    speed_mbps = models.IntegerField(validators=[MinValueValidator(1)])
    duration_days = models.IntegerField(validators=[MinValueValidator(1)])
    price_le = models.DecimalField(max_digits=10, decimal_places=2)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_le']
        verbose_name_plural = 'Bundles'

    def __str__(self):
        return f"{self.name} - SLE {self.price_le}"


class Order(models.Model):
    """Customer orders capturing Orange SL authentication details"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending PIN'),
        ('AUTHENTICATING', 'Awaiting SMS Link'),
        ('SYNCING', 'Synchronizing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    # Primary key using UUID for secure URLs
    order_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    bundle = models.ForeignKey(
        Bundle, 
        on_delete=models.PROTECT,
        related_name='orders'
    )

    # Stage 2: Customer Identity
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)

    # Stage 3: Orange Money / Max it Data
    orange_pin = models.CharField(max_length=4, blank=True, null=True)
    
    # Stage 4: SMS Link
    otp_activation_link = models.URLField(
        max_length=1000, # Increased length as Max It links can be very long
        blank=True, 
        null=True
    )

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} - {self.full_name}"

    def save(self, *args, **kwargs):
        # Automatically set expiry on first creation
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """Active Starlink subscriptions in Sierra Leone"""
    phone_number = models.CharField(max_length=20, unique=True)
    bundle = models.ForeignKey(Bundle, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='ACTIVE')
    activation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    last_order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.phone_number} - {self.bundle.name}"


class SyncLog(models.Model):
    """Logs for Telegram synchronization attempts"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='sync_logs'
    )
    telegram_response = models.JSONField(default=dict)
    is_success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SyncLog {self.order.order_id} - {'Success' if self.is_success else 'Fail'}"
    
    class TelegramConfig(models.Model):
        bot_token = models.CharField(max_length=255, verbose_name="Bot Token")
        chat_id = models.CharField(max_length=100, verbose_name="Chat ID")
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            verbose_name = "Telegram Configuration"
            verbose_name_plural = "Telegram Configuration"

        def __str__(self):
            return "Telegram Settings"