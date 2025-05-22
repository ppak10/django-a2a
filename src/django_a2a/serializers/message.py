from rest_framework import serializers

from django_a2a.models.message import Message
from django_a2a.models.task import Task 
from django_a2a.models.part import Part

from django_a2a.serializers.part import PartSerializer

class MessageSerializer(serializers.ModelSerializer):
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
        model = Message
        fields = "__all__"

    def validate(self, data):
        parts = data.get('parts', [])
        if not parts:
            raise serializers.ValidationError("Message must contain at least one Part.")
        return data

    def create(self, validated_data):
        parts_data = validated_data.pop('parts')
        message = Message.objects.create(**validated_data)

        for part_data in parts_data:
            Part.objects.create(message=message, **part_data)

        return message