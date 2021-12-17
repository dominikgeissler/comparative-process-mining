from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class ViewAboutTests(TestCase):
    def test_get_about(self):
        response = self.client.get(reverse("about_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is the about page.")
        
class ViewManageLogsTests(TestCase):
    def test_upload_correct_format(self):
        file = SimpleUploadedFile("file.csv", b"content", content_type="text/csv")
        response = self.client.post(reverse('manage_view'), {'log_file': file, 'action': 'upload'})
        self.assertContains(response, "Upload successful")

    def test_upload_wrong_format(self):
        file = SimpleUploadedFile("file.pdf", b"content", content_type="application/pdf")
        response = self.client.post(reverse('manage_view'), {'log_file': file, 'action': 'upload'})
        self.assertContains(response, "File extension not supported")
    
    def test_upload_no_file(self):
        response = self.client.post(reverse('manage_view'), {'action': 'upload'})
        self.assertContains(response, "Please add a log")

    def test_delete_no_file(self):
        response = self.client.post(reverse('manage_view'), {'action': 'delete'})
        self.assertContains(response, "Please select a log")
    
