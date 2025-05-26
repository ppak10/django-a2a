from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from uuid import uuid4

class Message(models.Model):
    """
    https://google.github.io/A2A/specification/#64-message-object
    """
    class MessageRole(models.TextChoices):
        USER = 'user', 'User'
        AGENT = 'agent', 'Agent'

    ##############
    # A2A Schema #
    ##############
    role = models.CharField(max_length=10, choices=MessageRole.choices)
    # `parts` are one to many, reference to message included Part model.
    metadata = models.JSONField(blank=True, null=True)
    # `referenceTaskIds` handled by serializer
    messageId = models.CharField(primary_key=True, max_length=255, unique=True, null=False, blank=False, default=uuid4)
    # `taskId` handled by serializer
    contextId = models.CharField(max_length=255, null=True, blank=True)
    kind = models.CharField(max_length=10, default="message", editable=False)

    ###################################
    # Additional Relations and Fields #
    ###################################
    # Can only assigned to one task
    # https://google.github.io/A2A/specification/#61-task-object
    task = models.ForeignKey(
        'Task', # string to avoid circular import
        on_delete=models.CASCADE,
        related_name='history',
        null=True,
        blank=True
    )

    # Ownership for user authentication.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Necessary for ordering
    created_on = models.DateTimeField(default=timezone.now) 
    
    # Should update when new parts are added
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message(role={self.role}, parts={self.parts.count()})"

    def clean(self):
        super().clean()
        if self.role not in dict(self.MessageRole.choices):
            raise ValidationError({"role": "Invalid role. Must be 'user' or 'agent'."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
