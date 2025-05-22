import pytest

from django.core.exceptions import ValidationError

from a2a.models.message import Message
from a2a.models.part import Part
from a2a.models.task import Task

@pytest.mark.django_db
def test_create_message_basic():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)
    Part.objects.create(type=Part.PartType.TEXT, text="Some text", message=message)

    assert task.history.count() == 1
    assert list(task.history.all()) == [message]
    assert message.role == "user"
    assert message.task == task

@pytest.mark.django_db
def test_invalid_role():
    task = Task.objects.create()

    with pytest.raises(ValidationError) as exc_info:
        Message.objects.create(role="not_valid_role", task=task)

    assert "role" in str(exc_info.value)

@pytest.mark.django_db
def test_multiple_messages_same_task():
    task = Task.objects.create()
    msg1 = Message.objects.create(role="user", task=task)
    msg2 = Message.objects.create(role="agent", task=task)

    # Messages can be made without parts via model but using a serializer, each
    # message should have at least one part.
    Part(type=Part.PartType.TEXT, text="Some text", message=msg1)
    Part(type=Part.PartType.TEXT, text="Some text", message=msg2)

    assert task.history.count() == 2
    assert list(task.history.all()) == [msg1, msg2]
