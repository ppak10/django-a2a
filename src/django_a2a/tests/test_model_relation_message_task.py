import pytest
from django.core.exceptions import ValidationError
from django_a2a.models import Message, FileContent, Part, Task

@pytest.mark.django_db
def test_part_clean_text_kind_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    Part.objects.create(kind=Part.PartKind.TEXT, text="Some text", message=message)

@pytest.mark.django_db
def test_part_clean_text_kind_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing text field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, message=message)
    assert "Text field is required when `kind` is 'text'." in str(excinfo.value)

    # text + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, text="valid", data={"key": "val"}, message=message)
    assert "Only `text` should be populated for `kind` 'text'." in str(excinfo.value)

    # text + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, text="valid", file=file_content, message=message)
    assert "Only `text` should be populated for `kind` 'text'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_data_kind_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, message=message)

@pytest.mark.django_db
def test_part_clean_data_kind_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing data field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, message=message)
    assert "Data field is required when `kind` is 'data'." in str(excinfo.value)

    # data + text populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, text="text", message=message)
    assert "Only `data` should be populated for `kind` 'data'." in str(excinfo.value)

    # data + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, file=file_content, message=message)
    assert "Only `data` should be populated for `kind` 'data'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_file_kind_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, message=message)

@pytest.mark.django_db
def test_part_clean_file_kind_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing file field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, message=message)
    assert "File field is required when `kind` is 'file'." in str(excinfo.value)

    # file + text populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, file=file_content, text="text", message=message)
    assert "Only `file` should be populated for `kind` 'file'." in str(excinfo.value)

    # file + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, file=file_content, data={"key": "val"}, message=message)
    assert "Only `file` should be populated for `kind` 'file'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_invalid_kind():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind="invalid_kind", message=message)
    assert "Invalid `kind`." in str(excinfo.value)

@pytest.mark.django_db
def test_create_valid_part_instances():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Text part
    Part.objects.create(kind=Part.PartKind.TEXT, text="hello", message=message)

    # Data part
    Part.objects.create(kind=Part.PartKind.DATA, data={"foo": "bar"}, message=message)

    # File part
    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, message=message)

@pytest.mark.django_db
def test_multiple_messages_same_task():
    task = Task.objects.create()

    # Adds messagesId manually here for ordering (uuid had random ordering)
    message_1 = Message.objects.create(messageId="a", role="user", task=task)
    message_2 = Message.objects.create(messageId="b", role="agent", task=task)

    Part.objects.create(kind=Part.PartKind.TEXT, text="Prompt", message=message_1)
    Part.objects.create(kind=Part.PartKind.TEXT, text="Response", message=message_2)

    history = list(task.history.prefetch_related('parts').order_by('created_on'))
    assert history[0].role == "user"
    assert history[0].parts.first().text == "Prompt"
    assert history[1].role == "agent"
    assert history[1].parts.first().text == "Response"
