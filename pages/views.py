import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Min, Max
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from listings.models import Property
from .forms import ContactForm

logger = logging.getLogger(__name__)

CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW_SECONDS = 3600


def home(request):
    available = Property.objects.filter(status=Property.Status.AVAILABLE)

    featured = list(available.filter(is_featured=True)[:6])
    if len(featured) < 3:
        featured = list(available.exclude(pk__in=[p.pk for p in featured])[: 6 - len(featured)]) + featured

    price_stats = available.aggregate(min_price=Min('price'), max_price=Max('price'))
    stats = {
        'total_listings': available.count(),
        'city_count': available.values('city').distinct().count(),
        'min_price': price_stats['min_price'],
        'max_price': price_stats['max_price'],
    }

    type_counts = dict(available.values_list('property_type').annotate(count=Count('id')))
    property_types = [
        {'value': value, 'label': label, 'count': type_counts.get(value, 0)}
        for value, label in Property.PropertyType.choices
    ]

    context = {
        'featured_properties': featured,
        'stats': stats,
        'property_types': property_types,
    }
    return render(request, 'pages/home.html', context)


def contact(request):
    if request.method == 'POST':
        rate_key = f'contact_submissions_{request.META.get("REMOTE_ADDR", "unknown")}'
        submission_count = cache.get(rate_key, 0)
        if submission_count >= CONTACT_RATE_LIMIT:
            messages.error(request, "You've submitted too many messages recently. Please try again later.")
            return redirect(reverse('pages:contact'))

        form = ContactForm(request.POST)
        if form.is_valid():
            cache.set(rate_key, submission_count + 1, CONTACT_RATE_WINDOW_SECONDS)
            contact_message = form.save()
            try:
                property_url = None
                if contact_message.property:
                    property_url = request.build_absolute_uri(contact_message.property.get_absolute_url())
                email_context = {'contact': contact_message, 'property_url': property_url}
                text_body = render_to_string('pages/emails/contact_notification.txt', email_context, request=request)
                html_body = render_to_string('pages/emails/contact_notification.html', email_context, request=request)

                email = EmailMultiAlternatives(
                    subject=f'New inquiry from {contact_message.name}',
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_TO_EMAIL],
                )
                email.attach_alternative(html_body, 'text/html')
                email.send(fail_silently=True)
            except Exception:
                logger.exception('Failed to send contact notification email for inquiry #%s', contact_message.pk)
            messages.success(request, "Thanks! We've received your message and will get back to you shortly.")
            return redirect(reverse('pages:contact'))
    else:
        initial = {}
        selected_property = None
        property_id = request.GET.get('property')
        if property_id:
            initial['property'] = property_id
            try:
                selected_property = Property.objects.filter(pk=int(property_id)).first()
            except (TypeError, ValueError):
                selected_property = None
        form = ContactForm(initial=initial)
        return render(request, 'pages/contact.html', {'form': form, 'selected_property': selected_property})

    return render(request, 'pages/contact.html', {'form': form})
