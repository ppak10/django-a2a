from uuid import UUID, uuid4
import pytest

from django.core.exceptions import ValidationError

from django_a2a.models.message import Message

# Just creates and tests the message model
# Although `parts` is technically required, this relationship will be tested in
# `test_message_part_model.py`
# Same applies to `task` and these are in `test_message_task_model.py`
@pytest.mark.django_db
def test_create_message_without_messageId():
    """
    Server should create a uuid for `messageId` by default
    """
    message = Message.objects.create(role="user")

    assert message.role == "user"
    assert isinstance(message.messageId, UUID)


@pytest.mark.django_db
def test_create_message_with_messageId():
    """
    Server should allow for `messageId` provided by user
    """
    message_id = uuid4()
    message = Message.objects.create(role="user", messageId=message_id)

    assert message.role == "user"
    assert message.messageId == message_id

@pytest.mark.django_db
def test_create_message_with_id():
    message = Message.objects.create(role="user", messageId="test")

    assert message.role == "user"
    assert message.messageId == "test"

@pytest.mark.django_db
def test_invalid_role():
    with pytest.raises(ValidationError) as exc_info:
        Message.objects.create(role="not_valid_role")

    assert "role" in str(exc_info.value)
