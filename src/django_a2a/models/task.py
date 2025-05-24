from uuid import uuid4
from django.db import models
from django.utils import timezone

from django_a2a.models.message import Message

class Task(models.Model):
    """
    https://google.github.io/A2A/specification/#61-task-object
    """
    ##############
    # A2A Schema #
    ##############
    id = models.UUIDField(primary_key=True, default=uuid4)
    contextId = models.CharField(max_length=255, null=True, blank=True, default=uuid4) # Should not be unique
    # `status` Task Status relationship assigned in TaskStatus model
    # `artifacts` Artifacts relationship assigned in Artifact model
    # `history` History relationship assigned in Message model
    metadata = models.JSONField(blank=True, null=True)

    # created_on and updated_on would be tracked externally here.

    def __str__(self):
        return f"Task Id:{self.id}"

    class Meta:
        ordering = ["id"]

class TaskStatus(models.Model):
    """
    https://google.github.io/A2A/specification/#62-taskstatus-object
    """

    class TaskState(models.TextChoices):
        """
        https://google.github.io/A2A/specification/#63-taskstate-enum
        """

        SUBMITTED = 'submitted', 'Submitted'  # Task received by server, acknowledged, but processing has not yet actively started.
        WORKING = 'working', 'Working'  # Task is actively being processed by the agent.
        INPUT_REQUIRED = 'input-required', 'Input Required'  # Agent requires additional input from the client/user to proceed.
        COMPLETED = 'completed', 'Completed'  # Task finished successfully.
        CANCELED = 'canceled', 'Canceled'  # Task was canceled by the client or server.
        FAILED = 'failed', 'Failed'  # Task terminated due to an error.
        REJECTED = 'rejected', 'Rejected'  # Task has be rejected by the remote agent (Terminal state).
        AUTH_REQUIRED = 'auth-required', 'Auth Required' # Authentication required from client/user to proceed. (Task is paused)
        UNKNOWN = 'unknown', 'Unknown'  # State cannot be determined (e.g., invalid or expired task ID).

    ##############
    # A2A Schema #
    ##############
    state = models.CharField(max_length=20, choices=TaskState.choices)
    message = models.OneToOneField(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_message'
    )
    timestamp = models.DateTimeField(default=timezone.now, null=True, blank=True)

    ###################################
    # Additional Relations and Fields #
    ###################################
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='status'
    )

    def __str__(self):
        return f"{self.state} @ {self.timestamp or 'no timestamp'}"
