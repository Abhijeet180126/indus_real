from django.contrib import admin
from .models import Property, PropertyImage, Amenity


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'listing_type', 'property_type', 'city', 'state', 'price', 'status', 'is_featured', 'created_at']
    list_filter = ['listing_type', 'property_type', 'status', 'is_featured', 'city', 'state']
    search_fields = ['title', 'address', 'city', 'state', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['amenities']
    inlines = [PropertyImageInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    search_fields = ['name']
