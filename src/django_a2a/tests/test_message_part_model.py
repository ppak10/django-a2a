import pytest
from django.core.exceptions import ValidationError
from a2a.models.part import Part, FileContent
from a2a.models.artifact import Artifact
from a2a.models.message import Message
from a2a.models.task import Task  # For creating tasks if needed

@pytest.mark.django_db
def test_file_content_clean_validation():
    # Valid: only bytes
    fc = FileContent(bytes="somebase64data")
    fc.clean()  # Should not raise

    # Valid: only uri
    fc = FileContent(uri="https://example.com/file")
    fc.clean()  # Should not raise

    # Invalid: both bytes and uri set
    fc = FileContent(bytes="data", uri="https://example.com/file")
    with pytest.raises(ValidationError) as excinfo:
        fc.clean()
    assert "Only one of `bytes` or `uri` may be non-null." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_text_type_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    Part.objects.create(type=Part.PartType.TEXT, text="Some text", message=message)

@pytest.mark.django_db
def test_part_clean_text_type_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing text field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.TEXT, message=message)
    assert "Text field is required when type is 'text'." in str(excinfo.value)

    # text + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.TEXT, text="valid", data={"key": "val"}, message=message)
    assert "Only `text` should be populated for type 'text'." in str(excinfo.value)

    # text + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.TEXT, text="valid", file=file_content, message=message)
    assert "Only `text` should be populated for type 'text'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_data_type_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    Part.objects.create(type=Part.PartType.DATA, data={"key": "value"}, message=message)

@pytest.mark.django_db
def test_part_clean_data_type_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing data field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.DATA, message=message)
    assert "Data field is required when type is 'data'." in str(excinfo.value)

    # data + text populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.DATA, data={"key": "value"}, text="text", message=message)
    assert "Only `data` should be populated for type 'data'." in str(excinfo.value)

    # data + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.DATA, data={"key": "value"}, file=file_content, message=message)
    assert "Only `data` should be populated for type 'data'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_file_type_valid():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(type=Part.PartType.FILE, file=file_content, message=message)

@pytest.mark.django_db
def test_part_clean_file_type_invalid_fields():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Missing file field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.FILE, message=message)
    assert "File field is required when type is 'file'." in str(excinfo.value)

    # file + text populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.FILE, file=file_content, text="text", message=message)
    assert "Only `file` should be populated for type 'file'." in str(excinfo.value)

    # file + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type=Part.PartType.FILE, file=file_content, data={"key": "val"}, message=message)
    assert "Only `file` should be populated for type 'file'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_invalid_type():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(type="invalid_type", message=message)
    assert "Invalid type." in str(excinfo.value)

@pytest.mark.django_db
def test_part_str_method():
    part = Part(type=Part.PartType.TEXT)
    assert str(part) == "Part(type=text)"

@pytest.mark.django_db
def test_create_valid_part_instances():
    task = Task.objects.create()
    message = Message.objects.create(role="user", task=task)

    # Text part
    Part.objects.create(type=Part.PartType.TEXT, text="hello", message=message)

    # Data part
    Part.objects.create(type=Part.PartType.DATA, data={"foo": "bar"}, message=message)

    # File part
    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(type=Part.PartType.FILE, file=file_content, message=message)
