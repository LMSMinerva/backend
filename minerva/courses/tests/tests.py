import base64
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from course_category.models.models import CourseCategory
from institution.models.models import Institution
from ..models.models import Course
from ..serializers.serializers import CourseSerializer


class CourseTests(APITestCase):
    """
    Test suite for the Course model and its API endpoints.
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

        self.category = CourseCategory.objects.create(name="Test Category")
        self.institution = Institution.objects.create(
            name="Test Institution",
            description="A sample institution for testing purposes.",
        )

        self.course_data = {
            "name": "Test Course",
            "alias": "test-course",
            "category": self.category,
            "institution": self.institution,
            "active": True,
            "description": "Test Description",
            "creation_date": "2023-01-01",
            "last_update": "2023-01-01",
            "modules_count": 5,
        }
        self.course = Course.objects.create(**self.course_data)

    def test_get_all_courses(self):
        """
        Test retrieving all courses.
        """
        response = self.client.get(reverse("course_list_create"))
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_course(self):
        """
        Test retrieving a single course by its id (UUID).
        """
        response = self.client.get(
            reverse("course_detail_update_delete", kwargs={"id": self.course.id})
        )
        course = Course.objects.get(id=self.course.id)
        serializer = CourseSerializer(course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_course(self):
        """
        Test creating a new course.
        """
        create_data = self.course_data.copy()
        create_data["institution"] = self.institution.id
        create_data["category"] = self.category.id
        response = self.client.post(
            reverse("course_list_create"), create_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Course.objects.get(id=response.data["id"]).name, "Test Course")

    def test_update_course(self):
        """
        Test updating an existing course.
        """
        updated_data = self.course_data.copy()
        updated_data["name"] = "Updated Course"
        updated_data["category"] = self.category.id
        updated_data["institution"] = self.institution.id
        response = self.client.put(
            reverse("course_detail_update_delete", kwargs={"id": self.course.id}),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")

    def test_partial_update_course(self):
        """
        Test partially updating an existing course.
        """
        partial_data = {"name": "Partially Updated Course"}
        response = self.client.put(
            reverse("course_detail_update_delete", kwargs={"id": self.course.id}),
            partial_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Partially Updated Course")

    def test_delete_course(self):
        """
        Test deleting an existing course.
        """
        response = self.client.delete(
            reverse("course_detail_update_delete", kwargs={"id": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)
