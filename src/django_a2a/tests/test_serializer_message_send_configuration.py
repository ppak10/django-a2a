from django_a2a.serializers import MessageSendConfigurationSerializer

# Sample valid data
VALID_DATA = {
    "acceptedOutputModes": ["text", "image"],
    "historyLength": 5,
    "pushNotificationConfig": {
        "endpoint": "https://example.com/notify",
        "enabled": True
    },
    "blocking": False
}


def test_valid_configuration():
    serializer = MessageSendConfigurationSerializer(data=VALID_DATA)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["acceptedOutputModes"] == ["text", "image"]
    assert serializer.validated_data["blocking"] is False


def test_missing_optional_fields():
    data = {
        "acceptedOutputModes": ["text"]
    }
    serializer = MessageSendConfigurationSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    assert "historyLength" not in serializer.validated_data
    assert "pushNotificationConfig" not in serializer.validated_data


def test_missing_required_field():
    data = {
        "blocking": True
    }
    serializer = MessageSendConfigurationSerializer(data=data)
    assert not serializer.is_valid()
    assert "acceptedOutputModes" in serializer.errors


def test_invalid_output_modes():
    data = {
        "acceptedOutputModes": "not-a-list"  # Should be a list of strings
    }
    serializer = MessageSendConfigurationSerializer(data=data)
    assert not serializer.is_valid()
    assert "acceptedOutputModes" in serializer.errors


def test_invalid_push_notification_config():
    data = {
        "acceptedOutputModes": ["text"],
        "pushNotificationConfig": {
            "endpoint": "not-a-url",
            "enabled": "yes"  # Should be a boolean
        }
    }
    serializer = MessageSendConfigurationSerializer(data=data)
    assert not serializer.is_valid()
    assert "pushNotificationConfig" in serializer.errors
