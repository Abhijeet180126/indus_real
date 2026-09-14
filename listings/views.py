from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import Property


def _parse_price(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def property_list(request):
    properties = Property.objects.filter(status=Property.Status.AVAILABLE)

    query = request.GET.get('q', '').strip()
    listing_type = request.GET.get('listing_type', '')
    property_type = request.GET.get('property_type', '')
    city = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if query:
        properties = properties.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
        )
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    if property_type:
        properties = properties.filter(property_type=property_type)
    if city:
        properties = properties.filter(city__icontains=city)
    min_price_val = _parse_price(min_price)
    max_price_val = _parse_price(max_price)
    if min_price_val is not None:
        properties = properties.filter(price__gte=min_price_val)
    if max_price_val is not None:
        properties = properties.filter(price__lte=max_price_val)

    paginator = Paginator(properties, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    cities = (
        Property.objects.filter(status=Property.Status.AVAILABLE)
        .exclude(city='')
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    context = {
        'page_obj': page_obj,
        'listing_types': Property.ListingType.choices,
        'property_types': Property.PropertyType.choices,
        'cities': cities,
        'filters': {
            'q': query,
            'listing_type': listing_type,
            'property_type': property_type,
            'city': city,
            'min_price': min_price,
            'max_price': max_price,
        },
    }
    return render(request, 'listings/property_list.html', context)


def property_detail(request, slug):
    property_obj = get_object_or_404(Property, slug=slug)
    return render(request, 'listings/property_detail.html', {'property': property_obj})
