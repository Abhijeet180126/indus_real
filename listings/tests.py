import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Property, PropertyImage

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def make_property(**kwargs):
    defaults = dict(
        title='Test Property',
        price=Decimal('100000'),
        address='123 Test St',
        city='Testville',
        state='Test State',
        area_sqft=1000,
        description='A nice place.',
    )
    defaults.update(kwargs)
    return Property.objects.create(**defaults)


class PropertyListViewTests(TestCase):
    def test_invalid_price_filters_are_ignored_not_crashed(self):
        make_property()
        response = self.client.get(reverse('listings:list'), {'min_price': 'abc', 'max_price': 'xyz'})
        self.assertEqual(response.status_code, 200)

    def test_valid_price_filters_narrow_results(self):
        cheap = make_property(title='Cheap', price=Decimal('50000'))
        pricey = make_property(title='Pricey', price=Decimal('900000'))
        response = self.client.get(reverse('listings:list'), {'min_price': '100000'})
        titles = [p.title for p in response.context['page_obj']]
        self.assertIn(pricey.title, titles)
        self.assertNotIn(cheap.title, titles)

    def test_keyword_search_matches_title_and_description(self):
        match = make_property(title='Sunny Beach House', description='Steps from the shore.')
        other = make_property(title='Downtown Loft', description='City views.')
        response = self.client.get(reverse('listings:list'), {'q': 'beach'})
        titles = [p.title for p in response.context['page_obj']]
        self.assertIn(match.title, titles)
        self.assertNotIn(other.title, titles)


class PropertyModelTests(TestCase):
    def test_slug_is_unique_for_duplicate_titles(self):
        p1 = make_property(title='Same Title')
        p2 = make_property(title='Same Title')
        self.assertNotEqual(p1.slug, p2.slug)

    def test_only_one_primary_image_per_property(self):
        prop = make_property()
        img1 = PropertyImage.objects.create(property=prop, image='test1.jpg', is_primary=True)
        img2 = PropertyImage.objects.create(property=prop, image='test2.jpg', is_primary=True)
        img1.refresh_from_db()
        self.assertFalse(img1.is_primary)
        self.assertTrue(img2.is_primary)
        self.assertEqual(prop.primary_image, img2)


def make_uploaded_image(width=3000, height=2000, fmt='JPEG', name='big.jpg'):
    buf = BytesIO()
    Image.new('RGB', (width, height), color='red').save(buf, format=fmt)
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=f'image/{fmt.lower()}')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PropertyImageResizeTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_oversized_image_is_downscaled_on_upload(self):
        prop = make_property()
        pi = PropertyImage.objects.create(property=prop, image=make_uploaded_image(3000, 2000))
        with Image.open(pi.image.path) as img:
            self.assertLessEqual(max(img.size), 1600)

    def test_small_image_is_left_untouched(self):
        prop = make_property()
        pi = PropertyImage.objects.create(property=prop, image=make_uploaded_image(400, 300))
        with Image.open(pi.image.path) as img:
            self.assertEqual(img.size, (400, 300))
