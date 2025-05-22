import pytest
from uuid import uuid4

from django_a2a.serializers.artifact import ArtifactSerializer
from django_a2a.models.task import Task

@pytest.mark.django_db
def test_artifact_serializer_valid_data():
    task = Task.objects.create()
    data = {
        "name": "Log Output",
        "description": "Standard output from script",
        "index": 0,
        "append": True,
        "last_chunk": False,
        "metadata": {"size": "1MB"},
        "task_id": task.id,
        "parts": [
            {
                'type': 'text',
                'text': 'This is a test part.'
            },
        ]
    }

    serializer = ArtifactSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    artifact = serializer.save()
    assert artifact.name == data["name"]
    assert str(artifact.task.id) == str(task.id)


@pytest.mark.django_db
def test_artifact_serializer_missing_optional_fields():
    task = Task.objects.create()
    data = {
        "task_id": task.id,
        "parts": [
            {
                'type': 'text',
                'text': 'This is a test part.'
            },
        ]
    }

    serializer = ArtifactSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    artifact = serializer.save()
    assert artifact.name is None
    assert artifact.index is 0
    assert artifact.append is None


@pytest.mark.django_db
def test_artifact_serializer_invalid_metadata():
    task = Task.objects.create()
    data = {
        "task_id": task.id,
        "parts": [
            {
                'type': 'text',
                'text': 'This is a test part.'
            },
        ],
        "metadata": "not a JSON object"
    }

    serializer = ArtifactSerializer(data=data)
    assert not serializer.is_valid()
    assert "metadata" in serializer.errors


@pytest.mark.django_db
def test_artifact_serializer_invalid_task_reference():
    data = {
        "task_id": 0,
        "parts": [
            {
                'type': 'text',
                'text': 'This is a test part.'
            },
        ],
    }

    serializer = ArtifactSerializer(data=data)
    assert not serializer.is_valid()
    assert "task_id" in serializer.errors
