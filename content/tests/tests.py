import base64
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from content.models.content import Content
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

        self.course = Course.objects.create(
            name="Test Course", description="Test Course Description"
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
        )
        self.Content_2 = Content.objects.create(
            module=self.module,
            name="Content 2",
            description="Content 2 Description",
        )

    def test_get_Contents_by_module(self):
        """
        Test to retrieve Contents by module_id.
        """
        url = reverse("content_list") + f"?module_id={self.module.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_Content(self):
        """
        Test to create a new Content.
        """
        url = reverse("content_list")
        data = {
            "module": self.module.id,
            "name": "Content 3",
            "description": "Content 3 Description",
        }
        response = self.client.post(url, data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Content 3")
        self.assertEqual(response.data["module"], self.module.id)

    def test_get_Content_by_id(self):
        """
        Test to retrieve a single Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Content 1")

    def test_update_Content(self):
        """
        Test to update a Content by UUID.
        """
        url = reverse("content_detail", kwargs={"id": self.Content_1.id})
        data = {"name": "Updated Content 1", "description": "Updated Description"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Content 1")

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
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 2)
