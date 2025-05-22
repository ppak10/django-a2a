from rest_framework import serializers

from django_a2a.models.artifact import Artifact
from django_a2a.models.message import Message
from django_a2a.models.part import Part
from django_a2a.models.task import Task, TaskStatus

from django_a2a.serializers.artifact import ArtifactSerializer
from django_a2a.serializers.message import MessageSerializer 

class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = "__all__"

class TaskSerializer(serializers.ModelSerializer):
    status = TaskStatusSerializer(required=False)
    artifacts = ArtifactSerializer(many=True, required=False)
    history = MessageSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = "__all__"
    
    def create(self, validated_data):
        artifacts_data = validated_data.pop('artifacts', [])
        history_data = validated_data.pop('history', [])
        status_data = validated_data.pop('status', None)

        task = Task.objects.create(**validated_data)

        if status_data:
            TaskStatus.objects.create(task=task, **status_data)

        for artifact in artifacts_data:
            parts = artifact.pop('parts', [])
            artifact_obj = Artifact.objects.create(task_id=task.id, **artifact)
            for part in parts:
                Part.objects.create(artifact=artifact_obj, **part)

        for message in history_data:
            parts = message.pop('parts', [])
            message_obj = Message.objects.create(task_id=task.id, **message)
            for part in parts:
                Part.objects.create(message=message_obj, **part)

        return task

