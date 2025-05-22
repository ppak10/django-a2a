from rest_framework import serializers

from a2a.models.part import FileContent, Part

class FileContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileContent
        fields = "__all__"

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
        fields = "__all__"
