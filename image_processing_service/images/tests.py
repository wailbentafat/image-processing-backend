from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import image
from django.contrib.auth.models import User
from PIL import Image
import io

class ImageAPITestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test image
        self.image_file = io.BytesIO()
        self.image = Image.new('RGB', (100, 100))
        self.image.save(self.image_file, format='PNG')
        self.image_file.name = 'test_image.png'
        self.image_file.seek(0)

    def test_upload_image(self):
        response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('url', response.data)

    def test_get_image(self):
        # First, upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Then, get the uploaded image
        response = self.client.get(f'/images/{image_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], image_id)

    def test_resize_image(self):
        # Upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Resize the image
        response = self.client.post(f'/resize/{image_id}/', {'width': 50, 'height': 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachment; filename="cropped_', response['Content-Disposition'])

    def test_crop_image(self):
        # Upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Crop the image
        response = self.client.post(f'/crop/{image_id}/', {'box': [10, 10, 50, 50]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachment; filename="cropped_', response['Content-Disposition'])

    def test_change_format(self):
        # Upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Change the format of the image
        response = self.client.post(f'/format/{image_id}/', {'format': 'JPEG'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachment; filename="cropped_', response['Content-Disposition'])

    def test_remove_background(self):
        # Upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Remove the background
        response = self.client.post(f'/remove_background/{image_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachment; filename="removed_', response['Content-Disposition'])

    def test_delete_image(self):
        # Upload an image
        upload_response = self.client.post('/upload/', {'image': self.image_file}, format='multipart')
        image_id = upload_response.data['id']

        # Delete the image
        response = self.client.delete(f'/images/{image_id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_all_images(self):
        # Upload an image
        self.client.post('/upload/', {'image': self.image_file}, format='multipart')

        # Get all images
        response = self.client.get('/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

