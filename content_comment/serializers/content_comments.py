from rest_framework import serializers
from content_comment.models import ContentComment


class ContentCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    is_reply = serializers.BooleanField(read_only=True)

    class Meta:
        model = ContentComment
        fields = [
            "id",
            "user",
            "content",
            "parent_comment",
            "comment",
            "comment_date",
            "is_reply",
            "replies",
        ]
        read_only_fields = ["id", "user", "comment_date", "is_reply"]

    def get_replies(self, obj):
        """Use model's get_replies method to fetch replies."""
        replies = obj.get_replies()
        return ContentCommentSerializer(replies, many=True).data

    def validate(self, data):
        if data.get("parent_comment") and self.instance:
            if str(data["parent_comment"].id) == str(self.instance.id):
                raise serializers.ValidationError("A comment cannot reply to itself.")
        return data
