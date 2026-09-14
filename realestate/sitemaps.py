from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from listings.models import Property


class PropertySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Property.objects.filter(status=Property.Status.AVAILABLE)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['pages:home', 'pages:contact', 'listings:list']

    def location(self, item):
        return reverse(item)
