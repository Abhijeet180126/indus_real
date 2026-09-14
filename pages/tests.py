from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def valid_payload(self, **overrides):
        payload = {
            'name': 'Jane Doe',
            'phone': '555-1234',
            'email': '',
            'message': 'Interested in a 3BHK.',
        }
        payload.update(overrides)
        return payload

    def test_invalid_property_param_does_not_crash(self):
        response = self.client.get(reverse('pages:contact'), {'property': 'not-a-number'})
        self.assertEqual(response.status_code, 200)

    def test_valid_submission_creates_message_and_redirects(self):
        response = self.client.post(reverse('pages:contact'), self.valid_payload())
        self.assertRedirects(response, reverse('pages:contact'))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_valid_submission_sends_notification_email(self):
        self.client.post(reverse('pages:contact'), self.valid_payload())
        self.assertEqual(len(mail.outbox), 1)

    def test_honeypot_field_rejects_submission_silently(self):
        response = self.client.post(reverse('pages:contact'), self.valid_payload(website='http://spam.example'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_rate_limit_blocks_excess_submissions(self):
        for _ in range(5):
            self.client.post(reverse('pages:contact'), self.valid_payload())
        self.assertEqual(ContactMessage.objects.count(), 5)

        response = self.client.post(reverse('pages:contact'), self.valid_payload(), follow=True)
        self.assertEqual(ContactMessage.objects.count(), 5)
        messages = [m.message for m in response.context['messages']]
        self.assertTrue(any('too many messages' in m for m in messages))
