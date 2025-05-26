from rest_framework import serializers

from django_a2a.models.artifact import Artifact
from django_a2a.models.message import Message
from django_a2a.models.part import Part
from django_a2a.models.task import Task, TaskStatus

from django_a2a.serializers.artifact import ArtifactSerializer
from django_a2a.serializers.message import MessageSerializer 

class TaskStatusSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        write_only=True,

        # required set to false for TaskStatusUpdateEventSerializer
        # TODO: Handle this more throughly.
        required=False
    )

    class Meta:
        model = TaskStatus
        exclude = ["id", "created_by", "created_on", "updated_on"]

class TaskSerializer(serializers.ModelSerializer):
    status = TaskStatusSerializer(required=False)
    artifacts = ArtifactSerializer(many=True, required=False)
    history = MessageSerializer(many=True, required=False)

    class Meta:
        model = Task
        exclude = ["created_by", "created_on", "updated_on"]
    
    def create(self, validated_data):
        artifacts_data = validated_data.pop('artifacts', [])
        history_data = validated_data.pop('history', [])
        status_data = validated_data.pop('status', {})

        task = Task.objects.create(**validated_data)

        status_data["task"] = task.id
        status_serializer = TaskStatusSerializer(data=status_data)
        status_serializer.is_valid(raise_exception=True)
        status_serializer.save()

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

class TaskStatusUpdateEventSerializer(serializers.Serializer):
    """
    For views and other methods for updating task status.
    https://google.github.io/A2A/specification/#722-taskstatusupdateevent-object
    """
    taskId = serializers.CharField()
    contextId = serializers.CharField()
    kind = serializers.ChoiceField(choices=["status-update"])
    status = TaskStatusSerializer()
    final = serializers.BooleanField(required=False, default=False)
    metadata = serializers.DictField(child=serializers.JSONField(), required=False)

    def validate(self, data):
        # Get the task instance using taskId
        try:
            task = Task.objects.get(id=data["taskId"])
        except Task.DoesNotExist:
            raise serializers.ValidationError({"taskId": "Task with this ID does not exist."})

        # Inject task into nested status data
        status_data = data.get("status", {})
        status_data["task"] = task.id
        print(status_data)

        # Re-validate status serializer with injected task
        status_serializer = TaskStatusSerializer(data=status_data)
        status_serializer.is_valid(raise_exception=True)
        data["status"] = status_serializer.validated_data

        return data
