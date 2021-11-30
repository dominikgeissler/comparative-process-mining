from django.test import TestCase
from django.urls import reverse

class AboutViewTests(TestCase):
    def test_get_about(self):
        response = self.client.get(reverse("about_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is the about page.")

