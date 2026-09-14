from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import path, include

from .sitemaps import PropertySitemap, StaticViewSitemap

admin.site.site_header = f'{settings.COMPANY_NAME} Administration'
admin.site.site_title = f'{settings.COMPANY_NAME} Admin'
admin.site.index_title = 'Site Administration'

sitemaps = {
    'properties': PropertySitemap,
    'static': StaticViewSitemap,
}


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


urlpatterns = [
    path('SecureAdmin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('properties/', include('listings.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
