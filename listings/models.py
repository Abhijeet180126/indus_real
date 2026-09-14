from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image, ImageOps

MAX_IMAGE_DIMENSION = 1600


class Amenity(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name_plural = 'amenities'
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    class ListingType(models.TextChoices):
        SALE = 'sale', 'For Sale'
        RENT = 'rent', 'For Rent'

    class PropertyType(models.TextChoices):
        HOUSE = 'house', 'House'
        APARTMENT = 'apartment', 'Apartment'
        VILLA = 'villa', 'Villa'
        PLOT = 'plot', 'Plot / Land'
        COMMERCIAL = 'commercial', 'Commercial'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        SOLD = 'sold', 'Sold'
        RENTED = 'rented', 'Rented'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    listing_type = models.CharField(max_length=10, choices=ListingType.choices, default=ListingType.SALE)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.HOUSE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='')

    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_sqft = models.PositiveIntegerField(help_text='Area in square feet')

    description = models.TextField()
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties')
    map_link = models.URLField(blank=True, help_text='Google Maps link (optional)')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    is_featured = models.BooleanField(default=False, help_text='Show on the home page')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'properties'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f'{base_slug}-{i}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('listings:detail', kwargs={'slug': self.slug})

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def directions_url(self):
        if self.map_link:
            return self.map_link
        if self.has_coordinates:
            return f'https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}'
        return ''

    @property
    def osm_embed_url(self):
        if not self.has_coordinates:
            return ''
        delta = 0.005
        lat, lng = float(self.latitude), float(self.longitude)
        bbox = f'{lng - delta},{lat - delta},{lng + delta},{lat + delta}'
        return f'https://www.openstreetmap.org/export/embed.html?bbox={bbox}&marker={lat},{lng}'


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f'Image for {self.property.title}'

    def save(self, *args, **kwargs):
        if self.is_primary:
            PropertyImage.objects.filter(property_id=self.property_id).exclude(pk=self.pk).update(is_primary=False)
        if self.image and not self.image._committed:
            self._downscale_image()
        super().save(*args, **kwargs)

    def _downscale_image(self):
        try:
            img = Image.open(self.image)
            img = ImageOps.exif_transpose(img)
            img_format = (img.format or 'JPEG').upper()
            if img.width <= MAX_IMAGE_DIMENSION and img.height <= MAX_IMAGE_DIMENSION:
                return
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
            if img_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format=img_format, quality=85, optimize=True)
            self.image = ContentFile(buffer.getvalue(), name=self.image.name)
        except Exception:
            pass
