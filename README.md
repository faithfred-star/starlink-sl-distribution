# Starlink Sierra Leone - Django Full-Stack Application

A complete Django full-stack application for Starlink internet bundles in Sierra Leone with Telegram bot integration, Stripe payment processing, and Orange Money support.

## Project Structure

```
starlink_django/
├── starlink_config/          # Django project settings
│   ├── settings.py          # Main Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── bundles/                 # Bundles app
│   ├── models.py            # Bundle, Order, Subscription models
│   ├── views.py             # Bundle API views
│   ├── urls.py              # Bundle URLs
│   ├── admin.py             # Django admin configuration
│   └── migrations/          # Database migrations
├── telegram_bot/            # Telegram bot app
│   ├── handlers.py          # Telegram bot handlers
│   ├── views.py             # Telegram webhook views
│   ├── urls.py              # Telegram URLs
│   └── migrations/          # Database migrations
├── payments/                # Payments app
│   ├── views.py             # Payment processing views
│   ├── urls.py              # Payment URLs
│   └── migrations/          # Database migrations
├── templates/               # HTML templates
│   └── payments/            # Payment templates
├── static/                  # Static files (CSS, JS, images)
├── .env                     # Environment variables (local)
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
└── README.md                # This file
```

## Features

### 1. **Bundle Management**
- Create and manage Starlink internet packages
- Support for different bundle types (Free Trial, Lite, Social, Power, Streamer, Elite)
- Pricing in Sierra Leone Leone (Le)
- Popular package highlighting

### 2. **Telegram Bot Integration**
- `/start` - Start the bot and browse packages
- `/help` - Get help and support information
- Browse packages directly in Telegram
- Phone number authentication
- Order creation and tracking
- Payment notifications

### 3. **Payment Processing**
- **Stripe Integration**: Full Stripe payment intent support
- **Orange Money**: Ready for Orange Money API integration
- Webhook handling for payment confirmations
- Payment logging and transaction tracking
- Subscription activation on successful payment

### 4. **Order Management**
- Create orders with automatic expiration (21 seconds)
- Track order status (Pending, Authenticated, Processing, Completed, Failed, Cancelled)
- Phone number verification
- Subscription activation

### 5. **API Endpoints**
- `GET /api/bundles/list/` - List all bundles
- `GET /api/bundles/<id>/` - Get bundle details
- `POST /api/bundles/create-order/` - Create new order
- `GET /api/bundles/order/<order_id>/` - Get order details
- `POST /api/payments/create-intent/` - Create Stripe payment intent
- `POST /api/payments/webhook/stripe/` - Stripe webhook handler
- `GET /api/payments/verify/` - Verify payment status
- `POST /api/telegram/webhook/` - Telegram webhook
- `GET /api/telegram/health/` - Bot health check

## Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Virtual environment support
- PostgreSQL (optional, SQLite for development)

### Step 1: Clone and Setup

```bash
cd /home/ubuntu/starlink_django
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/telegram/webhook/

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Orange Money
ORANGE_MONEY_API_KEY=your-api-key
ORANGE_MONEY_API_URL=https://api.orange.com/payment/v1

# WhatsApp
WHATSAPP_NUMBER=+1662408-7180
```

### Step 4: Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### Step 5: Load Initial Data

```bash
python manage.py shell
```

Then in the Django shell:

```python
from bundles.models import Bundle
from decimal import Decimal

Bundle.objects.create(
    name="Experience Pass",
    bundle_type="FREE",
    description="Free trial for 12 hours",
    data_gb="20 GB",
    speed_mbps=50,
    duration_days=0.5,  # 12 hours
    price_le=Decimal('0.00'),
    is_popular=False,
)

Bundle.objects.create(
    name="Lite Pass",
    bundle_type="LITE",
    description="Perfect for browsing",
    data_gb="10 GB",
    speed_mbps=100,
    duration_days=7,
    price_le=Decimal('49.00'),
    is_popular=False,
)

# Add more bundles...
```

### Step 6: Run Development Server

```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## Telegram Bot Setup

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create a new bot
4. Copy the bot token

### 2. Configure Webhook

Update your `.env` with the bot token:

```env
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/telegram/webhook/
```

### 3. Set Webhook (via API)

```bash
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/telegram/webhook/"}'
```

### 4. Test Bot

Search for your bot on Telegram and send `/start`

## Payment Integration

### Stripe Setup

1. Create Stripe account at https://stripe.com
2. Get API keys from dashboard
3. Update `.env`:

```env
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
```

4. Set webhook in Stripe dashboard:
   - Endpoint: `https://yourdomain.com/api/payments/webhook/stripe/`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`

### Orange Money Setup

1. Contact Orange Money for API credentials
2. Update `.env`:

```env
ORANGE_MONEY_API_KEY=your-api-key
ORANGE_MONEY_API_URL=https://api.orange.com/payment/v1
```

## API Usage Examples

### Get All Bundles

```bash
curl http://localhost:8000/api/bundles/list/
```

### Create Order

```bash
curl -X POST http://localhost:8000/api/bundles/create-order/ \
  -H "Content-Type: application/json" \
  -d '{
    "bundle_id": 1,
    "phone_number": "+232 76 123 456",
    "email": "user@example.com"
  }'
```

### Get Order Details

```bash
curl http://localhost:8000/api/bundles/order/ORD-ABC12345/
```

### Create Payment Intent

```bash
curl -X POST http://localhost:8000/api/payments/create-intent/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD-ABC12345"}'
```

## Admin Interface

Access Django admin at `http://localhost:8000/admin/`

- Manage bundles
- View orders and subscriptions
- Track payments
- Monitor user subscriptions

## Database Models

### Bundle
- name, bundle_type, description
- data_gb, speed_mbps, duration_days
- price_le, is_popular, is_active

### Order
- order_id, bundle_id, phone_number
- status, total_amount, payment_method
- transaction_id, verification_code
- created_at, expires_at

### Subscription
- phone_number, bundle_id
- status, activation_date, expiry_date
- data_used_gb, last_order

### PaymentLog
- order_id, payment_gateway
- amount, status, transaction_id
- response_data, error_message

## Environment Variables

See `.env.example` for complete list. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `DEBUG` | Django debug mode | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key | Yes |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Yes |
| `WHATSAPP_NUMBER` | WhatsApp contact number | No |

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn starlink_config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "starlink_config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:

```bash
docker build -t starlink-sl .
docker run -p 8000:8000 --env-file .env starlink-sl
```

## Logging

Logs are stored in `logs/django.log` with rotation settings:
- Max file size: 15MB
- Backup count: 10 files

Configure log level in `.env`:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Telegram Webhook Not Working
- Check bot token is correct
- Verify webhook URL is accessible from internet
- Check firewall/security group settings
- Test webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

### Stripe Payment Failing
- Verify API keys are correct
- Check webhook signature secret
- Review Stripe logs in dashboard
- Test with Stripe test cards

### Database Issues
- Run migrations: `python manage.py migrate`
- Check database connection in `.env`
- For PostgreSQL, ensure database exists

## Support

- **WhatsApp**: +1 (662) 408-7180
- **Email**: support@starlink-sl.com
- **Telegram**: @StarlinkSierraLeone

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Changelog

### Version 1.0.0 (2026-05-11)
- Initial release
- Telegram bot integration
- Stripe payment processing
- Bundle management system
- Order tracking
- Subscription management
