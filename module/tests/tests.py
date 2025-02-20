import base64
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from content.models.content import Content
from content.serializers.content import ContentSerializer
from content_category.models.content_category import ContentCategory
from course.models import Course
from module.models import Module
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


class ModuleTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Generar token JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.course = Course.objects.create(
            name="Test Course", description="Test Course Description"
        )
        self.content_category = ContentCategory.objects.create(name="video")
        self.module_1 = Module.objects.create(
            course=self.course,
            name="Module 1",
            description="Module 1 Description",
        )
        self.module_2 = Module.objects.create(
            course=self.course,
            name="Module 2",
            description="Module 2 Description",
        )

        self.content_1 = Content.objects.create(
            module=self.module_1,
            name="Content 1",
            description="Content 1 Description",
            content_type=self.content_category,
        )
        self.content_2 = Content.objects.create(
            module=self.module_1,
            name="Content 2",
            description="Content 2 Description",
            content_type=self.content_category,
        )

    def test_get_ordered_contents(self):
        """
        Test retrieving contents of a module in ordered sequence.
        """
        response = self.client.get(
            reverse("module_contents", kwargs={"id": self.module_1.id})
        )
        expected_contents = [self.content_1, self.content_2]
        serializer = ContentSerializer(expected_contents, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_modules_by_course(self):
        """
        Test to retrieve modules by course_id.
        """
        url = reverse("module_list") + f"?course_id={self.course.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_module(self):
        """
        Test to create a new module.
        """
        url = reverse("module_list")
        data = {
            "course": self.course.id,
            "name": "Module 3",
            "description": "Module 3 Description",
        }
        response = self.client.post(url, data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Module 3")
        self.assertEqual(response.data["course"], self.course.id)

    def test_get_module_by_id(self):
        """
        Test to retrieve a single module by UUID.
        """
        url = reverse("module_detail", kwargs={"id": self.module_1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Module 1")

    def test_update_module(self):
        """
        Test to update a module by UUID.
        """
        url = reverse("module_detail", kwargs={"id": self.module_1.id})
        data = {"name": "Updated Module 1", "description": "Updated Description"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Module 1")

    def test_delete_module(self):
        """
        Test to delete a module by UUID.
        """
        url = reverse("module_detail", kwargs={"id": self.module_1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_field_on_create(self):
        """
        Test to ensure the 'order' field is automatically assigned correctly.
        """
        url = reverse("module_list")
        data = {
            "course": str(self.course.id),
            "name": "Module 3",
            "description": "Module 3 Description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 3)

    def test_order_field_on_delete(self):
        """
        Test to ensure the 'order' field is updated correctly after a module is deleted.
        """
        self.module_2.delete()
        self.module_1.refresh_from_db()
        self.assertEqual(self.module_1.order, 1)
        url = reverse("module_list")
        data = {
            "course": str(self.course.id),
            "name": "Module 3",
            "description": "Module 3 Description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 2)
