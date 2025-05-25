import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError

from django_a2a.models.task import Task, TaskStatus
from django_a2a.models.message import Message

@pytest.mark.django_db
def test_task_status_default_state():
    task = Task.objects.create()
    status = TaskStatus.objects.create(task=task)

    assert status.state == TaskStatus.TaskState.SUBMITTED
    assert status.task == task
    assert status.timestamp is not None

@pytest.mark.django_db
@pytest.mark.parametrize("state", [
    TaskStatus.TaskState.SUBMITTED,
    TaskStatus.TaskState.WORKING,
    TaskStatus.TaskState.INPUT_REQUIRED,
    TaskStatus.TaskState.COMPLETED,
    TaskStatus.TaskState.CANCELED,
    TaskStatus.TaskState.FAILED,
    TaskStatus.TaskState.REJECTED,
    TaskStatus.TaskState.AUTH_REQUIRED,
    TaskStatus.TaskState.UNKNOWN,
])
def test_valid_task_states(state):
    task = Task.objects.create()
    status = TaskStatus.objects.create(task=task, state=state)

    assert status.state == state

@pytest.mark.django_db
def test_invalid_task_state_raises_error():
    task = Task.objects.create()
    status = TaskStatus(task=task, state="invalid-state")

    with pytest.raises(ValidationError):
        status.full_clean()  # This is what actually triggers the validation
