import json
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from content.models.content import Content
from content_category.models.content_category import ContentCategory
from course.models.course import Course
from module.models import Module
from content_interaction.models.content_interaction import ContentInteraction


class ContentInteractionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        self.course = Course.objects.create(
            name="Test Course", description="Test Course Description"
        )
        self.module = Module.objects.create(
            course=self.course,
            name="Test Module",
            description="Test Module Description",
        )
        self.content_category = ContentCategory.objects.create(name="video")

        self.content = Content.objects.create(
            module=self.module,
            name="Test Content",
            description="Test Content Description",
            metadata=150,
            body="https://youtube.com",
            content_type=self.content_category,
        )

        self.content1 = Content.objects.create(
            module=self.module,
            name="Test Content",
            description="Test Content Description",
            metadata=250,
            body="https://youtube.com",
            content_type=self.content_category,
        )

        self.content2 = Content.objects.create(
            module=self.module,
            name="Test Content",
            description="Test Content Description",
            metadata=250,
            body="https://youtube.com",
            content_type=self.content_category,
        )

        self.interaction = ContentInteraction.objects.create(
            content=self.content, user=self.user, completed=False, rating=3
        )

        self.interaction1 = ContentInteraction.objects.create(
            content=self.content1, user=self.user, completed=True, rating=5
        )

    def test_get_all_interactions(self):
        url = reverse("content_interaction_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_filtered_interactions(self):
        url = reverse("content_interaction_list") + f"?content={self.content.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_interaction(self):
        url = reverse("content_interaction_list")
        self.assertEqual(self.content2.reviews, 0)
        data = {
            "content": str(self.content2.id),
            "user": self.user.id,
            "completed": True,
            "rating": 2,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Refresca desde la base de datos para obtener los valores actualizados
        self.content2.refresh_from_db()

        self.assertEqual(self.content2.reviews, 1)
        self.assertEqual(response.data["rating"], 2)
        self.assertEqual(response.data["completed"], True)

    def test_create_interaction_negative_rating(self):
        url = reverse("content_interaction_list")
        data = {
            "content": str(self.content2.id),
            "user": self.user.id,
            "completed": True,
            "rating": -1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_interaction_zero_rating(self):
        url = reverse("content_interaction_list")
        data = {
            "content": str(self.content2.id),
            "user": self.user.id,
            "completed": True,
            "rating": 0,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_interaction_more_five_rating(self):
        url = reverse("content_interaction_list")
        data = {
            "content": str(self.content2.id),
            "user": self.user.id,
            "completed": True,
            "rating": 6,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_interaction_invalid_content_id(self):
        url = reverse("content_interaction_list")
        data = {
            "content": "00000000-0000-0000-0000-000000000000",
            "user": self.user.id,
            "completed": True,
            "rating": 4,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_interaction(self):
        url = reverse("content_interaction_detail", kwargs={"id": self.interaction.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed"], False)
        self.assertEqual(response.data["rating"], 3)

    def test_update_interaction_complete(self):
        url = reverse("content_interaction_detail", kwargs={"id": self.interaction.id})
        data = {"completed": True, "rating": 4}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed"], True)
        self.assertEqual(response.data["rating"], 4)

    def test_update_interaction_partial(self):
        url = reverse("content_interaction_detail", kwargs={"id": self.interaction.id})
        data = {"rating": 5}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed"], False)
        self.assertEqual(response.data["rating"], 5)

    def test_delete_interaction(self):
        url = reverse("content_interaction_detail", kwargs={"id": self.interaction.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ContentInteraction.objects.filter(id=self.interaction.id).exists()
        )

    def test_content_rating_and_reviews_update(self):
        """Test that content rating and reviews are updated after updating an interaction."""
        initial_reviews = self.content.reviews
        initial_rating = self.content.rating or 0
        url = reverse("content_interaction_detail", kwargs={"id": self.interaction.id})
        data = {"completed": True, "rating": 5}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh content from DB
        self.content.refresh_from_db()

        self.assertEqual(self.content.reviews, initial_reviews)
        expected_avg = round((initial_rating - 3 + 5), 2)
        self.assertEqual(float(self.content.rating), expected_avg)
