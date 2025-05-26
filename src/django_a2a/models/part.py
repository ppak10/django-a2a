from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from django_a2a.models.artifact import Artifact
from django_a2a.models.message import Message

class FileContent(models.Model):
    """
    https://google.github.io/A2A/specification/#66-filecontent-object
    """
    ##############
    # A2A Schema #
    ##############
    name = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)

    # TODO: Update this into two different file types of either FileWithBytes
    # or FileWithUri similar to how the Parts model is structured.
    # Adhere to v0.2.1
    # https://google.github.io/A2A/specification/#661-filewithbytes-object
    # https://google.github.io/A2A/specification/#662-filewithuri-object
    bytes = models.TextField(blank=True, null=True)
    uri = models.URLField(blank=True, null=True)

    ###################################
    # Additional Relations and Fields #
    ###################################
    # Ownership for user authentication.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created_on = models.DateTimeField(default=timezone.now) 

    def clean(self):
        if self.bytes and self.uri:
            raise ValidationError("Only one of `bytes` or `uri` may be non-null.")

    def __str__(self):
        return self.name or self.uri or "Unnamed File"

class Part(models.Model):
    class PartKind(models.TextChoices):
        """
        https://google.github.io/A2A/specification/#65-part-union-type
        """
        TEXT = 'text'
        FILE = 'file'
        DATA = 'data'

    ##############
    # A2A Schema #
    ##############
    kind = models.CharField(max_length=10, choices=PartKind.choices)
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


    ###################################
    # Additional Relations and Fields #
    ###################################
    # A Part is created through an Artifact
    # Can only assigned to one artifact
    artifact = models.ForeignKey(
        Artifact,
        to_field="artifactId",
        on_delete=models.CASCADE,
        related_name='parts',
        null=True,
        blank=True
    )

    # A Part is created through a Message
    # Can only assigned to one message
    message = models.ForeignKey(
        Message,
        to_field="messageId",
        on_delete=models.CASCADE,
        related_name='parts',
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

    created_on = models.DateTimeField(default=timezone.now) 

    # Should update when new parts are added
    updated_on = models.DateTimeField(default=timezone.now)

    def clean(self):
        super().clean()
        # Ensure only fields relevant to `kind` are populated
        if self.kind == 'text':
            if not self.text:
                raise ValidationError("Text field is required when `kind` is 'text'.")
            if self.data or self.file:
                raise ValidationError("Only `text` should be populated for `kind` 'text'.")
        elif self.kind == 'data':
            if self.text or self.file:
                raise ValidationError("Only `data` should be populated for `kind` 'data'.")
            if self.data is None:
                raise ValidationError("Data field is required when `kind` is 'data'.")
        elif self.kind == 'file':
            if not self.file:
                raise ValidationError("File field is required when `kind` is 'file'.")
            if self.text or self.data:
                raise ValidationError("Only `file` should be populated for `kind` 'file'.")
        else:
            raise ValidationError("Invalid `kind`.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Part(kind={self.kind})"