from rest_framework import serializers

from a2a.models.artifact import Artifact
from a2a.models.part import Part
from a2a.models.task import Task

from rest_framework import serializers
from a2a.serializers.part import PartSerializer

class ArtifactSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True)

    # Used in creating new message.
    # Does not provide `task` data during read.
    # No `task` serialization, causes circular import error.
    task_id = serializers.PrimaryKeyRelatedField(
        source='task',
        queryset=Task.objects.all(),
        write_only=True,

        # Include if writing directly, otherwise inferred from task serializer.
        required=False,
    )

    class Meta:
        model = Artifact
        fields = "__all__"

    def validate_metadata(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("metadata must be a JSON object")
        return value

    def validate(self, data):
        parts = data.get('parts', [])
        if not parts:
            raise serializers.ValidationError("Artifact must contain at least one Part.")
        return data

    def create(self, validated_data):
        parts_data = validated_data.pop('parts')
        artifact = Artifact.objects.create(**validated_data)

        for part_data in parts_data:
            Part.objects.create(artifact=artifact, **part_data)

        return artifact 