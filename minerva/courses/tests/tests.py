import base64
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from course_category.models import CourseCategory
from institution.models import Institution
from courses.models import Course
from courses.serializers import CourseSerializer


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

        # Create course data with only essential fields
        self.course_data = {
            "name": "Test Course",
            "alias": "test-course",
            "category": self.category,
            "institution": self.institution,
            "modules": 5,
            "description": "Test Description",
        }
        self.course = Course.objects.create(**self.course_data)

    def test_get_all_courses(self):
        """
        Test to ensure retrieving all courses works correctly.
        """
        response = self.client.get(reverse("course_list_create"))
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_course(self):
        """
        Test to confirm that a new course can be created successfully without sending default fields.
        """
        create_data = {
            "name": "Test Course 2",
            "alias": "test-course-2",
            "category": self.category.id,
            "institution": self.institution.id,
            "modules": 5,
            "description": "Test Description",
        }
        response = self.client.post(
            reverse("course_list_create"), create_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(
            Course.objects.get(id=response.data["id"]).name, "Test Course 2"
        )

    def test_get_single_course(self):
        """
        Test to verify retrieving a single course by its ID returns the correct information.
        """
        response = self.client.get(
            reverse("course_detail_by_id", kwargs={"id": self.course.id})
        )
        course = Course.objects.get(id=self.course.id)
        serializer = CourseSerializer(course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_course(self):
        """
        Test to ensure only necessary fields are updated for existing courses.
        """
        updated_data = {
            "name": "Updated Course",
            "category": self.category.id,
            "institution": self.institution.id,
            "modules": 10,
        }
        response = self.client.put(
            reverse("course_detail_by_id", kwargs={"id": self.course.id}),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")
        self.assertEqual(self.course.modules, 10)

    def test_partial_update_course(self):
        """
        Test to confirm partial updates apply only to the specified fields.
        """
        partial_data = {"name": "Partially Updated Course"}
        response = self.client.put(
            reverse("course_detail_by_id", kwargs={"id": self.course.id}),
            partial_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Partially Updated Course")

    def test_delete_course(self):
        """
        Test to confirm that an existing course can be successfully deleted.
        """
        response = self.client.delete(
            reverse("course_detail_by_id", kwargs={"id": self.course.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    def test_get_single_course_by_slug(self):
        """
        Test to verify retrieving a single course by its slug returns the correct information.
        """
        response = self.client.get(
            reverse("course_detail_by_slug", kwargs={"alias": "test-course"})
        )
        course = Course.objects.get(alias="test-course")
        serializer = CourseSerializer(course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_course_by_slug(self):
        """
        Test to ensure an existing course can be updated using its slug.
        """
        updated_data = {
            "name": "Updated Course",
            "alias": "uc",
            "category": self.category.id,
            "institution": self.institution.id,
            "modules": 10,
            "active": False,
        }
        response = self.client.put(
            reverse("course_detail_by_slug", kwargs={"alias": "test-course"}),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")
        self.assertEqual(self.course.modules, 10)

    def test_partial_update_course_by_slug(self):
        """
        Test to ensure partial updates are possible using slug.
        """
        partial_data = {"name": "Partially Updated Course"}
        response = self.client.put(
            reverse("course_detail_by_slug", kwargs={"alias": "test-course"}),
            partial_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Partially Updated Course")

    def test_delete_course_by_slug(self):
        """
        Test to confirm that a course can be deleted using its slug.
        """
        response = self.client.delete(
            reverse("course_detail_by_slug", kwargs={"alias": "test-course"})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(alias="test-course").exists())

    def test_delete_course_by_nonexistent_slug(self):
        """
        Test to confirm attempting to delete a non-existent slug returns 404.
        """
        response = self.client.delete(
            reverse("course_detail_by_slug", kwargs={"alias": "nonexistent-slug"})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
