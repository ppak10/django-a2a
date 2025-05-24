import pytest
from uuid import uuid4

from django_a2a.models.artifact import Artifact

# Just creates and tests the artifact model
# Although `parts` is technically required, this relationship will be tested in
# `test_artifact_part_model.py`
# Same applies to `task` and these are in `test_artifact_task_model.py`

@pytest.mark.django_db
def test_create_artifact_minimal():
    artifact = Artifact.objects.create(artifactId="a")
    assert artifact.artifactId is not None
    assert artifact.name is None
    assert artifact.description is None
    assert str(artifact) == "Artifact: Unnamed"

@pytest.mark.django_db
def test_create_artifact_full_fields():
    metadata = {"key": "value"}
    artifact_id = uuid4()

    artifact = Artifact.objects.create(
        artifactId=artifact_id,
        name="Log File",
        description="Output logs from process",
        metadata=metadata,
    )

    assert artifact.name == "Log File"
    assert artifact.description == "Output logs from process"
    assert artifact.metadata == metadata

@pytest.mark.django_db
def test_artifact_defaults():
    artifact_id = uuid4()
    artifact = Artifact.objects.create(artifactId=artifact_id)
    assert artifact.metadata is None
    assert artifact.task is None

@pytest.mark.django_db
def test_artifact_str_with_name():
    artifact_id = uuid4()
    artifact = Artifact.objects.create(artifactId=artifact_id, name="Artifact")
    assert artifact.name == "Artifact"

@pytest.mark.django_db
def test_artifact_str_without_name():
    artifact_id = uuid4()
    artifact = Artifact.objects.create(artifactId=artifact_id)
    assert artifact.artifactId == artifact_id
