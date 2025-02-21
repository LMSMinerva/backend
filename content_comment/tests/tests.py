from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from content.models.content import Content
from content_category.models.content_category import ContentCategory
from content_comment.models import ContentComment
from course.models.course import Course
from module.models.module import Module


class ContentCommentTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
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
        self.comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Test comment"
        )

    def test_create_comment(self):
        url = reverse("content_comment_list")
        self.content.refresh_from_db()
        self.assertEqual(self.content.comments, 1)
        data = {
            "content": str(self.content.id),
            "user": self.user.id,
            "comment": "This is a test comment.",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.content.refresh_from_db()
        self.assertEqual(self.content.comments, 2)
        self.assertEqual(response.data["comment"], "This is a test comment.")

    def test_create_comment_invalid_content(self):
        url = reverse("content_comment_list")
        data = {
            "content": "00000000-0000-0000-0000-000000000000",
            "user": self.user.id,
            "comment": "Invalid content test.",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reply_comment(self):
        url = reverse("content_comment_list")
        data = {
            "content": str(self.content.id),
            "user": self.user.id,
            "parent_comment": str(self.comment.id),
            "comment": "Reply to parent.",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.content.refresh_from_db()
        self.assertEqual(self.content.comments, 2)

    def test_create_reply_invalid_parent(self):
        url = reverse("content_comment_list")
        data = {
            "content": str(self.content.id),
            "user": self.user.id,
            "parent_comment": "00000000-0000-0000-0000-000000000000",
            "comment": "Invalid parent reply.",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reply_to_self(self):
        url = reverse("content_comment_detail", kwargs={"id": self.comment.id})
        data = {
            "content": str(self.content.id),
            "user": self.user.id,
            "parent_comment": str(self.comment.id),
            "comment": "Self-reply.",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_comment_by_owner(self):
        comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Delete test."
        )
        url = reverse("content_comment_detail", kwargs={"id": comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.content.refresh_from_db()
        self.assertEqual(self.content.comments, 1)

    def test_delete_comment_by_non_owner(self):
        comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Non-owner delete test."
        )
        refresh = RefreshToken.for_user(self.other_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )
        url = reverse("content_comment_detail", kwargs={"id": comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments(self):
        ContentComment.objects.create(
            content=self.content, user=self.user, comment="Comment 1."
        )
        ContentComment.objects.create(
            content=self.content, user=self.user, comment="Comment 2."
        )
        url = reverse("content_comment_list")
        response = self.client.get(url, {"content": str(self.content.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_update_comment_partial(self):
        comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Original comment."
        )
        url = reverse("content_comment_detail", kwargs={"id": comment.id})
        data = {"comment": "Updated comment."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.comment, "Updated comment.")

    def test_update_comment_all(self):
        url = reverse("content_comment_detail", kwargs={"id": self.comment.id})
        data = {
            "content": str(self.content.id),
            "user": self.user.id,
            "comment": "Updated all",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, "Updated all")

    def test_get_replies_of_comment(self):
        parent_comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Parent comment."
        )
        reply1 = ContentComment.objects.create(
            content=self.content,
            user=self.user,
            comment="First reply.",
            parent_comment=parent_comment,
        )
        reply2 = ContentComment.objects.create(
            content=self.content,
            user=self.user,
            comment="Second reply.",
            parent_comment=parent_comment,
        )
        unrelated_comment = ContentComment.objects.create(
            content=self.content, user=self.user, comment="Unrelated comment."
        )
        url = reverse("comment_replies", kwargs={"id": parent_comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        reply_comments = [comment["comment"] for comment in response.data]
        self.assertIn("First reply.", reply_comments)
        self.assertIn("Second reply.", reply_comments)
        self.assertNotIn("Unrelated comment.", reply_comments)
