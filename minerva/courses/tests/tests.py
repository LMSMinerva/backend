import base64
from rest_framework.test import APIClient,APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from ..models.models import Course
from ..serializers.serializers import CourseSerializer

class CourseTests(APITestCase):
    """
    Test suite for the Course model and its API endpoints.
    """

    def setUp(self):
        """
        Set up the test client and create a sample course for testing.

        This method is called before each test case.

        Attributes:
            client (APIClient): The test client for making API requests.
            course_data (dict): The data for creating a sample course.
            course (Course): The sample course created for testing.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        credentials = base64.b64encode(b'testuser:testpassword').decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + credentials)
        self.course_data = {
            'name': 'Test Course',
            'alias': 'test-course',
            'category': 'Test Category',
            'visibility': True,
            'description': 'Test Description',
            'creation_date': '2023-01-01',
        }
        self.course = Course.objects.create(**self.course_data)

    def test_get_all_courses(self):
        """
        Test retrieving all courses.

        This test ensures that the API endpoint for retrieving all courses
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The response data matches the serialized course data.
        """
        response = self.client.get(reverse('course_list_create'))
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_course(self):
        """
        Test retrieving a single course by its primary key.

        This test ensures that the API endpoint for retrieving a single course
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The response data matches the serialized course data.
        """
        response = self.client.get(reverse('course_detail_update_delete', kwargs={'pk': self.course.pk}))
        course = Course.objects.get(pk=self.course.pk)
        serializer = CourseSerializer(course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_course(self):
        """
        Test creating a new course.

        This test ensures that the API endpoint for creating a new course
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 201.
            The created course's name matches the input data.
        """
        response = self.client.post(reverse('course_list_create'), self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Course.objects.get(pk=response.data['id']).name, 'Test Course')

    def test_update_course(self):
        """
        Test updating an existing course.

        This test ensures that the API endpoint for updating a course
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The updated course's name matches the input data.
        """
        updated_data = self.course_data.copy()
        updated_data['name'] = 'Updated Course'
        response = self.client.put(reverse('course_detail_update_delete', kwargs={'pk': self.course.pk}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Updated Course')

    def test_partial_update_course(self):
        """
        Test partially updating an existing course.

        This test ensures that the API endpoint for partially updating a course
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The partially updated course's name matches the input data.
        """
        partial_data = {'name': 'Partially Updated Course'}
        response = self.client.put(reverse('course_detail_update_delete', kwargs={'pk': self.course.pk}), partial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Partially Updated Course')

    def test_delete_course(self):
        """
        Test deleting an existing course.

        This test ensures that the API endpoint for deleting a course
        returns the correct status code and that the course is removed from the database.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 204.
        """
        response = self.client.delete(reverse('course_detail_update_delete', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)