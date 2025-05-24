from django.db import models
from django.utils import timezone
from uuid import uuid4

from django_a2a.models.task import Task

class Artifact(models.Model):
    ##############
    # A2A Schema #
    ##############
    # https://google.github.io/A2A/specification/#67-artifact-object
    artifactId = models.CharField(primary_key=True, max_length=255, unique=True, null=False, blank=False, default=uuid4)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # `parts` Parts are one to many, reference to artifact included Part model.
    metadata = models.JSONField(null=True, blank=True)

    ###################################
    # Additional Relations and Fields #
    ###################################
    # Can only assigned to one task
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='artifacts',
        null=True,
        blank=True
    )

    # Necessary for ordering
    created_on = models.DateTimeField(default=timezone.now) 

    # Should update when new parts are added
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Artifact: {self.name or 'Unnamed'}"
