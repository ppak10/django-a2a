import pytest
from django_a2a.models.task import Task
from django_a2a.serializers import MessageSendParamsSerializer

@pytest.mark.django_db
def test_valid_message_send_params_with_all_fields():
    task = Task.objects.create()

    data = {
        "message": {
            "role": "user",
            "task_id": task.id,
            "parts": [
                {
                    "kind": "text",
                    "text": "hi",
                }
            ]
        },
        "configuration": {
            "acceptedOutputModes": ["text", "image"],
            "historyLength": 10,
            "pushNotificationConfig": {
                "endpoint": "https://example.com/hook",
                "enabled": True
            },
            "blocking": False
        },
        "metadata": {
            "custom_key": "custom_value",
            "request_id": 123
        }
    }

    serializer = MessageSendParamsSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    validated = serializer.validated_data

    assert validated["message"]["parts"][0]["text"] == "hi"
    assert validated["configuration"]["blocking"] is False
    assert validated["metadata"]["request_id"] == 123


@pytest.mark.django_db
def test_valid_message_send_params_with_minimal_fields():
    task = Task.objects.create()

    data = {
        "message": {
            "role": "user",
            "task_id": task.id,
            "parts": [
                {
                    "kind": "data",
                    "data": {
                        "text": "hi"
                    }
                }
            ]
        }
    }

    serializer = MessageSendParamsSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    assert "configuration" not in serializer.validated_data
    assert "metadata" not in serializer.validated_data


@pytest.mark.django_db
def test_invalid_message_send_params_missing_parts():
    task = Task.objects.create()

    data = {
        "message": {
            "role": "user",
            "task_id": task.id,
            "parts": []  # Invalid: must have at least one part
        }
    }

    serializer = MessageSendParamsSerializer(data=data)
    assert not serializer.is_valid()
    assert "message" in serializer.errors
    assert "non_field_errors" in serializer.errors["message"]


@pytest.mark.django_db
def test_invalid_configuration_structure():
    data = {
        "message": {
            "role": "user",
            "task": 1,  # This assumes task=1 exists, would fail without DB setup
            "parts": [
                {"kind": "text", "text": "ok"}
            ]
        },
        "configuration": {
            "acceptedOutputModes": "text",  # Should be a list, not a string
        }
    }

    serializer = MessageSendParamsSerializer(data=data)
    assert not serializer.is_valid()
    assert "configuration" in serializer.errors
