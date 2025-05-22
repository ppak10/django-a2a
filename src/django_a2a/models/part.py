from django.db import models
from django.core.exceptions import ValidationError

from a2a.models.artifact import Artifact
from a2a.models.message import Message

class FileContent(models.Model):
    """
    https://google.github.io/A2A/specification/#66-filecontent-object
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    bytes = models.TextField(blank=True, null=True)
    uri = models.URLField(blank=True, null=True)

    def clean(self):
        if self.bytes and self.uri:
            raise ValidationError("Only one of `bytes` or `uri` may be non-null.")

    def __str__(self):
        return self.name or self.uri or "Unnamed File"

class Part(models.Model):
    class PartType(models.TextChoices):
        """
        https://google.github.io/A2A/specification/#65-part-union-type
        """
        TEXT = 'text'
        FILE = 'file'
        DATA = 'data'

    type = models.CharField(max_length=10, choices=PartType.choices)

    # Shared optional metadata
    metadata = models.JSONField(blank=True, null=True)

    # Text fields
    # https://google.github.io/A2A/specification/#651-textpart-object
    text = models.TextField(blank=True, null=True)
    
    # Data fields
    # https://google.github.io/A2A/specification/#653-datapart-object
    data = models.JSONField(blank=True, null=True)

    # File fields
    # https://google.github.io/A2A/specification/#652-filepart-object
    file = models.OneToOneField(FileContent, on_delete=models.CASCADE, blank=True, null=True)


    # A Part is created through an Artifact
    # Can only assigned to one artifact
    artifact = models.ForeignKey(
        Artifact,
        on_delete=models.CASCADE,
        related_name='parts',
        null=True,
        blank=True
    )

    # A Part is created through a Message
    # Can only assigned to one message
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='parts',
        null=True,
        blank=True
    )

    def clean(self):
        super().clean()
        # Ensure only fields relevant to `type` are populated
        if self.type == 'text':
            if not self.text:
                raise ValidationError("Text field is required when type is 'text'.")
            if self.data or self.file:
                raise ValidationError("Only `text` should be populated for type 'text'.")
        elif self.type == 'data':
            if self.text or self.file:
                raise ValidationError("Only `data` should be populated for type 'data'.")
            if self.data is None:
                raise ValidationError("Data field is required when type is 'data'.")
        elif self.type == 'file':
            if not self.file:
                raise ValidationError("File field is required when type is 'file'.")
            if self.text or self.data:
                raise ValidationError("Only `file` should be populated for type 'file'.")
        else:
            raise ValidationError("Invalid type.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Part(type={self.type})"