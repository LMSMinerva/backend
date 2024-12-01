import base64
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from ..models.models import Institution
from ..serializers.serializers import InstitutionSerializer


class InstitutionTests(APITestCase):
    """
    Test suite for the Institution model and its API endpoints.
    """

    def setUp(self):
        """
        Set up the test client and create sample data for testing.

        This method is called before each test case.

        Attributes:
            client (APIClient): The test client for making API requests.
            institution_data (dict): The data for creating a sample institution.
            institution (Institution): The sample institution created for testing.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        credentials = base64.b64encode(b"testuser:testpassword").decode("utf-8")
        self.client.credentials(HTTP_AUTHORIZATION="Basic " + credentials)
        self.institution_data = {
            "name": "Test Institution",
            "description": "A sample institution for testing purposes.",
            "url": "https://example.com",
            "image": "test_image.png",
            "icon": "test_icon.png",
        }
        self.institution = Institution.objects.create(**self.institution_data)

    def test_get_all_institutions(self):
        """
        Test retrieving all institutions.

        This test ensures that the API endpoint for retrieving all institutions
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The response data matches the serialized institution data.
        """
        response = self.client.get(reverse("institution_list_create"))
        institutions = Institution.objects.all()
        serializer = InstitutionSerializer(institutions, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_institution(self):
        """
        Test retrieving a single institution by its UUID.

        This test ensures that the API endpoint for retrieving a single institution
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The response data matches the serialized institution data.
        """
        response = self.client.get(
            reverse(
                "institution_detail_update_delete", kwargs={"id": self.institution.id}
            )
        )
        institution = Institution.objects.get(id=self.institution.id)
        serializer = InstitutionSerializer(institution)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_institution(self):
        """
        Test creating a new institution.

        This test ensures that the API endpoint for creating a new institution
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 201.
            The created institution's name matches the input data.
        """
        response = self.client.post(
            reverse("institution_list_create"), self.institution_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Institution.objects.count(), 2)
        self.assertEqual(
            Institution.objects.get(id=response.data["id"]).name, "Test Institution"
        )

    def test_update_institution(self):
        """
        Test updating an existing institution.

        This test ensures that the API endpoint for updating an institution
        returns the correct data and status code.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 200.
            The updated institution's name matches the input data.
        """
        updated_data = self.institution_data.copy()
        updated_data["name"] = "Updated Institution"
        response = self.client.put(
            reverse(
                "institution_detail_update_delete", kwargs={"id": self.institution.id}
            ),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.institution.refresh_from_db()
        self.assertEqual(self.institution.name, "Updated Institution")

    def test_delete_institution(self):
        """
        Test deleting an existing institution.

        This test ensures that the API endpoint for deleting an institution
        returns the correct status code and that the institution is removed from the database.

        Args:
            client (APIClient): The test client for making API requests.

        Asserts:
            The response status code is 204.
        """
        response = self.client.delete(
            reverse(
                "institution_detail_update_delete", kwargs={"id": self.institution.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Institution.objects.count(), 0)
