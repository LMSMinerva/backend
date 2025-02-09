from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from content_category.models import ContentCategory
from content_category.serializers import ContentCategorySerializer
import base64


class ContentCategoryTests(APITestCase):
    """
    Test suite for the ContentCategory model and its API endpoints.
    """

    def setUp(self):
        """
        Set up the test client and create sample data for testing.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        credentials = base64.b64encode(b"testuser:testpassword").decode("utf-8")
        self.client.credentials(HTTP_AUTHORIZATION="Basic " + credentials)

        self.content_category_data = {"name": "Test Category"}
        self.content_category = ContentCategory.objects.create(
            **self.content_category_data
        )

    def test_get_all_content_categories(self):
        """
        Test retrieving all content categories.
        """
        response = self.client.get(reverse("content_category_list_create"))
        content_categories = ContentCategory.objects.all()
        serializer = ContentCategorySerializer(content_categories, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_content_category(self):
        """
        Test retrieving a single content category by its UUID.
        """
        response = self.client.get(
            reverse(
                "content_category_detail_update_delete",
                kwargs={"id": self.content_category.id},
            )
        )
        content_category = ContentCategory.objects.get(id=self.content_category.id)
        serializer = ContentCategorySerializer(content_category)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_content_category(self):
        """
        Test creating a new content category.
        """
        self.content_category_new = {"name": "Test Category 2"}
        response = self.client.post(
            reverse("content_category_list_create"),
            self.content_category_new,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContentCategory.objects.count(), 2)
        self.assertEqual(
            ContentCategory.objects.get(id=response.data["id"]).name,
            "Test Category 2",
        )

    def test_update_content_category(self):
        """
        Test updating an existing content category.
        """
        updated_data = self.content_category_data.copy()
        updated_data["name"] = "Updated Category"
        response = self.client.put(
            reverse(
                "content_category_detail_update_delete",
                kwargs={"id": self.content_category.id},
            ),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content_category.refresh_from_db()
        self.assertEqual(self.content_category.name, "Updated Category")

    def test_delete_content_category(self):
        """
        Test deleting an existing content category.
        """
        response = self.client.delete(
            reverse(
                "content_category_detail_update_delete",
                kwargs={"id": self.content_category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ContentCategory.objects.count(), 0)
