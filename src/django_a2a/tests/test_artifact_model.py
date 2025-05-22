import pytest
from django_a2a.models.artifact import Artifact
from django_a2a.models.task import Task

@pytest.mark.django_db
def test_create_artifact_minimal():
    artifact = Artifact.objects.create(index=1)
    assert artifact.id is not None
    assert artifact.index == 1
    assert artifact.name is None
    assert str(artifact) == "Artifact: Unnamed (index=1)"

@pytest.mark.django_db
def test_create_artifact_full_fields():
    task = Task.objects.create()
    metadata = {"key": "value"}

    artifact = Artifact.objects.create(
        name="Log File",
        description="Output logs from process",
        index=0,
        append=True,
        last_chunk=False,
        metadata=metadata,
        task=task
    )

    assert artifact.name == "Log File"
    assert artifact.description == "Output logs from process"
    assert artifact.index == 0
    assert artifact.append is True
    assert artifact.last_chunk is False
    assert artifact.metadata == metadata
    assert artifact.task == task
    assert str(artifact) == "Artifact: Log File (index=0)"

@pytest.mark.django_db
def test_artifact_defaults():
    artifact = Artifact.objects.create()
    assert artifact.index == 0
    assert artifact.append is None
    assert artifact.last_chunk is None
    assert artifact.metadata is None
    assert artifact.task is None

@pytest.mark.django_db
def test_artifact_str_with_name():
    artifact = Artifact.objects.create(name="Build Report", index=5)
    assert str(artifact) == "Artifact: Build Report (index=5)"

@pytest.mark.django_db
def test_artifact_str_without_name():
    artifact = Artifact.objects.create(index=2)
    assert str(artifact) == "Artifact: Unnamed (index=2)"
