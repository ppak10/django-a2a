import pytest
from django.core.exceptions import ValidationError
from django_a2a.models import Message, FileContent, Part

@pytest.mark.django_db
def test_part_clean_text_kind_valid():
    message = Message.objects.create(role="user")

    Part.objects.create(kind=Part.PartKind.TEXT, text="Some text", message=message)

@pytest.mark.django_db
def test_part_clean_text_kind_invalid_fields():
    message = Message.objects.create(role="user")

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
    message = Message.objects.create(role="user")

    Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, message=message)

@pytest.mark.django_db
def test_part_clean_data_kind_invalid_fields():
    message = Message.objects.create(role="user")

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
    message = Message.objects.create(role="user")

    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, message=message)

@pytest.mark.django_db
def test_part_clean_file_kind_invalid_fields():
    message = Message.objects.create(role="user")

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
    message = Message.objects.create(role="user")

    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind="invalid_kind", message=message)
    assert "Invalid `kind`." in str(excinfo.value)

@pytest.mark.django_db
def test_create_valid_part_instances():
    message = Message.objects.create(role="user")

    # Text part
    Part.objects.create(kind=Part.PartKind.TEXT, text="hello", message=message)

    # Data part
    Part.objects.create(kind=Part.PartKind.DATA, data={"foo": "bar"}, message=message)

    # File part
    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, message=message)
