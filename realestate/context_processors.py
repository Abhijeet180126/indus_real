from django.conf import settings


def site_settings(request):
    return {
        'CURRENCY_SYMBOL': settings.CURRENCY_SYMBOL,
        'COMPANY_NAME': settings.COMPANY_NAME,
        'COMPANY_TAGLINE': settings.COMPANY_TAGLINE,
        'COMPANY_ADDRESS': settings.COMPANY_ADDRESS,
        'COMPANY_PHONE': settings.COMPANY_PHONE,
        'COMPANY_WHATSAPP': settings.COMPANY_WHATSAPP,
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'COMPANY_WEBSITE': settings.COMPANY_WEBSITE,
    }
