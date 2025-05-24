import pytest
from django.core.exceptions import ValidationError
from django_a2a.models import Artifact, FileContent, Part, Task

@pytest.mark.django_db
def test_part_clean_text_kind_valid():
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

    Part.objects.create(kind=Part.PartKind.TEXT, text="Some text", artifact=artifact)

@pytest.mark.django_db
def test_part_clean_text_kind_invalid_fields():
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

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
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

    Part.objects.create(kind=Part.PartKind.DATA, data={"key": "value"}, artifact=artifact)

@pytest.mark.django_db
def test_part_clean_data_kind_invalid_fields():
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

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
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, artifact=artifact)

@pytest.mark.django_db
def test_part_clean_file_kind_invalid_fields():
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

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
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

    with pytest.raises(ValidationError) as excinfo:
        Part.objects.create(kind="invalid_kind", artifact=artifact)
    assert "Invalid `kind`." in str(excinfo.value)

@pytest.mark.django_db
def test_create_valid_part_instances():
    task = Task.objects.create()
    artifact = Artifact.objects.create(task=task)

    # Text part
    Part.objects.create(kind=Part.PartKind.TEXT, text="hello", artifact=artifact)

    # Data part
    Part.objects.create(kind=Part.PartKind.DATA, data={"foo": "bar"}, artifact=artifact)

    # File part
    file_content = FileContent.objects.create(name="file.txt")
    Part.objects.create(kind=Part.PartKind.FILE, file=file_content, artifact=artifact)

@pytest.mark.django_db
def test_multiple_artifacts_same_task():
    task = Task.objects.create()
    artifact_1 = Artifact.objects.create(task=task)
    artifact_2 = Artifact.objects.create(task=task)

    Part(kind=Part.PartKind.TEXT, text="Some text", artifact=artifact_1)
    Part(kind=Part.PartKind.TEXT, text="Some text", artifact=artifact_2)

    assert task.artifacts.count() == 2
    assert list(task.artifacts.all()) == [artifact_1, artifact_2]

@pytest.mark.django_db
def test_multiple_artifacts_same_task():
    task = Task.objects.create()

    # Adds artifactId manually here for ordering (uuid had random ordering)
    artifact_1 = Artifact.objects.create(artifactId="a", name="a", task=task)
    artifact_2 = Artifact.objects.create(artifactId="b", name="b", task=task)

    Part.objects.create(kind=Part.PartKind.TEXT, text="Prompt", artifact=artifact_1)
    Part.objects.create(kind=Part.PartKind.TEXT, text="Response", artifact=artifact_2)

    artifacts = list(task.artifacts.prefetch_related('parts').order_by('created_on'))
    assert artifacts[0].name == "a"
    assert artifacts[0].parts.first().text == "Prompt"
    assert artifacts[1].name == "b"
    assert artifacts[1].parts.first().text == "Response"