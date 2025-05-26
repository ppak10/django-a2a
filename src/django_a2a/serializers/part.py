from rest_framework import serializers

from django_a2a.models import FileContent, Part, Message

class FileContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileContent
        exclude = ["id", "created_by", "created_on"]

class PartSerializer(serializers.ModelSerializer):
    # TODO: Handle integration of file upload to bucket.
    file = FileContentSerializer(read_only=True)
    file_id = serializers.PrimaryKeyRelatedField(
        source='file',
        queryset=FileContent.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Part
        exclude = ["id", "created_by", "created_on", "message"]
