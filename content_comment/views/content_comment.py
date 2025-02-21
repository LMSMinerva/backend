from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from content_comment.models import ContentComment
from content_comment.serializers.content_comments import ContentCommentSerializer


class ContentCommentListView(APIView):
    """
    List and create content comments.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses=ContentCommentSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="content",
                type=OpenApiTypes.UUID,
                description="UUID of the content to filter comments.",
                required=True,
            )
        ],
    )
    def get(self, request):
        """
        Retrieve all comments for a specific content.
        """
        content_id = request.query_params.get("content")
        if not content_id:
            return Response(
                {"detail": "Content ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = ContentComment.objects.filter(
            content_id=content_id, parent_comment__isnull=True
        )
        serializer = ContentCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(request=ContentCommentSerializer, responses=ContentCommentSerializer)
    def post(self, request):
        """
        Create a new comment or reply to an existing comment.
        """
        serializer = ContentCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentCommentDetailView(APIView):
    """
    Retrieve, update, or delete a specific content comment.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentCommentSerializer)
    def get(self, request, id):
        """
        Retrieve a specific comment by UUID.
        """
        comment = get_object_or_404(ContentComment, id=id)
        serializer = ContentCommentSerializer(comment)
        return Response(serializer.data)

    @extend_schema(request=ContentCommentSerializer, responses=ContentCommentSerializer)
    def put(self, request, id):
        """
        Update an existing comment by UUID.
        """
        comment = get_object_or_404(ContentComment, id=id)
        if comment.user != request.user:
            return Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ContentCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a comment by UUID.
        """
        comment = get_object_or_404(ContentComment, id=id)
        if comment.user != request.user:
            return Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentRepliesView(APIView):
    """
    List all replies to a specific comment.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentCommentSerializer(many=True))
    def get(self, request, id):
        """
        Retrieve all replies for a specific comment.
        """
        parent_comment = get_object_or_404(ContentComment, id=id)
        replies = parent_comment.get_replies()
        serializer = ContentCommentSerializer(replies, many=True)
        return Response(serializer.data)
