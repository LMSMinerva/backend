import base64
import json
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from content.models.content import Content
from content_category.models.content_category import ContentCategory
from course.models.course import Course
from module.models import Module
from django.urls import reverse


class ContentTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        credentials = base64.b64encode(b"testuser:testpassword").decode("utf-8")
        self.client.credentials(HTTP_AUTHORIZATION="Basic " + credentials)

        self.content_category1 = {"name": "codigo"}
        self.codigo = ContentCategory.objects.create(**self.content_category1)
        self.content_category2 = {"name": "pdf"}
        self.pdf = ContentCategory.objects.create(**self.content_category2)
        self.content_category3 = {"name": "video"}
        self.video = ContentCategory.objects.create(**self.content_category3)

        self.course = Course.objects.create(
            name="Test Course",
            description="Test Course Description",
        )
        self.module = Module.objects.create(
            course=self.course,
            name="Test module",
            description="Test module Description",
        )
        self.Content_1 = Content.objects.create(
            module=self.module,
            name="Content 1",
            description="Content 1 Description",
            metadata=150,
            body="https://youtube.com",
            content_type=self.video,
        )
        self.Content_2 = Content.objects.create(
            module=self.module,
            name="Content 2",
            description="Content 2 Description",
            metadata=3,
            body="https://drive.com",
            content_type=self.pdf,
        )

    def test_create_video_content(self):
        """
        Test to create a new video content.
        """
        url = reverse("content_list")
        data = {
            "module": self.module.id,
            "name": "Content video",
            "description": "Content video Description",
            "metadata": 250,
            "body": "https://youtube.com",
            "content_type": self.video.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Content video")
        self.assertEqual(response.data["content_type"], self.video.id)

    def test_create_pdf_content(self):
        """
        Test to create a new pdf content.
        """
        url = reverse("content_list")
        data = {
            "module": self.module.id,
            "name": "Content pdf",
            "description": "Content pdf Description",
            "metadata": 3,
            "body": "https://drive.google.com/file/d/1k1fcpMb5OxMXTEJ2U3ymAE5wTnDyvCRu/view?usp=sharing",
            "content_type": self.pdf.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Content pdf")
        self.assertEqual(
            response.data["body"],
            "https://drive.google.com/file/d/1k1fcpMb5OxMXTEJ2U3ymAE5wTnDyvCRu/view?usp=sharing",
        )
        self.assertEqual(response.data["content_type"], self.pdf.id)

    def test_create_codigo_content(self):
        """
        Test to create a new codigo content.
        """
        url = reverse("content_list")
        data = {
            "module": self.module.id,
            "name": "Content codigo",
            "description": "Content codigo Description",
            "metadata": {"lenguajes": ["python", "java", "c++"]},
            "body": "https://pdf.com",
            "content_type": self.codigo.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Content codigo")
        self.assertEqual(
            response.data["metadata"]["lenguajes"], ["python", "java", "c++"]
        )
        self.assertEqual(response.data["content_type"], self.codigo.id)

    def test_update_partial_content(self):
        """
        Test to update partial a Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        data = {"name": "Updated Content 1"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Content 1")
        self.assertEqual(response.data["description"], "Content 1 Description")

    def test_update_all_content(self):
        """
        Test to fully update a Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        data = {
            "module": self.module.id,
            "name": "Updated Content 1",
            "description": "Updated Description",
            "metadata": 200,
            "body": "https://youtube2.com",
            "content_type": self.video.id,
        }
        response = self.client.put(url, data, format="json")  # PUT para actualizar todo

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Content 1")
        self.assertEqual(response.data["description"], "Updated Description")
        self.assertEqual(response.data["metadata"], 200)
        self.assertEqual(response.data["body"], "https://youtube2.com")

    def test_get_Contents_by_module(self):
        """
        Test to retrieve Contents by module_id.
        """
        url = reverse("content_list") + f"?module_id={self.module.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_Content_by_id(self):
        """
        Test to retrieve a single Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Content 1")

    def test_delete_Content(self):
        """
        Test to delete a Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_field_on_create(self):
        """
        Test to ensure the 'order' field is automatically assigned correctly.
        """
        url = reverse("content_list")
        data = {
            "module": str(self.module.id),
            "name": "Content 3",
            "description": "Content 3 Description",
            "metadata": 2,
            "body": "https://drive.com",
            "content_type": self.pdf.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 3)

    def test_order_field_on_delete(self):
        """
        Test to ensure the 'order' field is updated correctly after a Content is deleted.
        """
        self.Content_2.delete()
        self.Content_1.refresh_from_db()
        self.assertEqual(self.Content_1.order, 1)
        url = reverse("content_list")
        data = {
            "module": str(self.module.id),
            "name": "Content 3",
            "description": "Content 3 Description",
            "metadata": 3,
            "body": "https://drive.com",
            "content_type": self.pdf.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 2)
