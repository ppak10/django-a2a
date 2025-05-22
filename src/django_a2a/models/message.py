from django.db import models
from django.core.exceptions import ValidationError

class Message(models.Model):
    """
    https://google.github.io/A2A/specification/#64-message-object
    """
    class MessageRole(models.TextChoices):
        USER = 'user', 'User'
        AGENT = 'agent', 'Agent'


    role = models.CharField(max_length=10, choices=MessageRole.choices)
    metadata = models.JSONField(blank=True, null=True)

    # Can only assigned to one task
    # https://google.github.io/A2A/specification/#61-task-object
    task = models.ForeignKey(
        'Task', # string to avoid circular import
        on_delete=models.CASCADE,
        related_name='history',
        null=True,
        blank=True
    )

    # Parts are one to many, reference to artifact included Part model.

    def __str__(self):
        return f"Message(role={self.role}, parts={self.parts.count()})"

    def clean(self):
        super().clean()
        if self.role not in dict(self.MessageRole.choices):
            raise ValidationError({"role": "Invalid role. Must be 'user' or 'agent'."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
