from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from course_category.models import CourseCategory
from course_category.serializers import CourseCategorySerializer
import base64


class CourseCategoryTests(APITestCase):
    """
    Test suite for the CourseCategory model and its API endpoints.
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

        self.course_category_data = {"name": "Test Category"}
        self.course_category = CourseCategory.objects.create(
            **self.course_category_data
        )

    def test_get_all_course_categories(self):
        """
        Test retrieving all course categories.
        """
        response = self.client.get(reverse("course_category_list_create"))
        course_categories = CourseCategory.objects.all()
        serializer = CourseCategorySerializer(course_categories, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_course_category(self):
        """
        Test retrieving a single course category by its UUID.
        """
        response = self.client.get(
            reverse(
                "course_category_detail_update_delete",
                kwargs={"id": self.course_category.id},
            )
        )
        course_category = CourseCategory.objects.get(id=self.course_category.id)
        serializer = CourseCategorySerializer(course_category)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_course_category(self):
        """
        Test creating a new course category.
        """
        self.course_category_new = {"name": "Test Category 2"}
        response = self.client.post(
            reverse("course_category_list_create"),
            self.course_category_new,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseCategory.objects.count(), 2)
        self.assertEqual(
            CourseCategory.objects.get(id=response.data["id"]).name,
            "Test Category 2",
        )

    def test_update_course_category(self):
        """
        Test updating an existing course category.
        """
        updated_data = self.course_category_data.copy()
        updated_data["name"] = "Updated Category"
        response = self.client.put(
            reverse(
                "course_category_detail_update_delete",
                kwargs={"id": self.course_category.id},
            ),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course_category.refresh_from_db()
        self.assertEqual(self.course_category.name, "Updated Category")

    def test_delete_course_category(self):
        """
        Test deleting an existing course category.
        """
        response = self.client.delete(
            reverse(
                "course_category_detail_update_delete",
                kwargs={"id": self.course_category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CourseCategory.objects.count(), 0)
