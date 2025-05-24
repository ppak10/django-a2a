import pytest
from django.core.exceptions import ValidationError
from django_a2a.models import Artifact, FileContent, Part

@pytest.mark.django_db
def test_part_clean_text_kind_valid():
    artifact = Artifact.objects.create()
    Part.objects.create(kind=Part.PartKind.TEXT, text="text", artifact=artifact)

    assert artifact.parts.first().kind == Part.PartKind.TEXT
    assert artifact.parts.first().text == "text" 

@pytest.mark.django_db
def test_part_clean_text_kind_invalid_fields():
    artifact = Artifact.objects.create()

    # Missing text field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, artifact=artifact)
    assert "Text field is required when `kind` is 'text'." in str(excinfo.value)

    # text + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, text="valid", data={"key": "val"}, artifact=artifact)
    assert "Only `text` should be populated for `kind` 'text'." in str(excinfo.value)

    # text + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.TEXT, text="valid", file=file_content, artifact=artifact)
    assert "Only `text` should be populated for `kind` 'text'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_data_kind_valid():
    artifact = Artifact.objects.create()

    Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, artifact=artifact)

@pytest.mark.django_db
def test_part_clean_data_kind_invalid_fields():
    artifact = Artifact.objects.create()

    # Missing data field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, artifact=artifact)
    assert "Data field is required when `kind` is 'data'." in str(excinfo.value)

    # data + text populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, text="text", artifact=artifact)
    assert "Only `data` should be populated for `kind` 'data'." in str(excinfo.value)

    # data + file populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, file=file_content, artifact=artifact)
    assert "Only `data` should be populated for `kind` 'data'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_file_kind_valid():
    artifact = Artifact.objects.create()

    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, artifact=artifact)

@pytest.mark.django_db
def test_part_clean_file_kind_invalid_fields():
    artifact = Artifact.objects.create()

    # Missing file field
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, artifact=artifact)
    assert "File field is required when `kind` is 'file'." in str(excinfo.value)

    # file + text populated
    file_content = FileContent.objects.create(name="file.txt")
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, file=file_content, text="text", artifact=artifact)
    assert "Only `file` should be populated for `kind` 'file'." in str(excinfo.value)

    # file + data populated
    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind=Part.PartKind.FILE, file=file_content, data={"key": "val"}, artifact=artifact)
    assert "Only `file` should be populated for `kind` 'file'." in str(excinfo.value)

@pytest.mark.django_db
def test_part_clean_invalid_kind():
    artifact = Artifact.objects.create()

    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind="invalid_kind", artifact=artifact)
    assert "Invalid `kind`." in str(excinfo.value)

@pytest.mark.django_db
def test_create_valid_part_instances():
    artifact = Artifact.objects.create()

    # Text part
    Part.objects.create(kind=Part.PartKind.TEXT, text="hello", artifact=artifact)

    # Data part
    Part.objects.create(kind=Part.PartKind.DATA, data={"foo": "bar"}, artifact=artifact)

    # File part
    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, artifact=artifact)
