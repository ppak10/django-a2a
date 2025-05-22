from django.db import models

from django_a2a.models.task import Task

class Artifact(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    index = models.PositiveIntegerField(default=0)
    append = models.BooleanField(null=True, blank=True)
    last_chunk = models.BooleanField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    # Can only assigned to one task
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='artifacts',
        null=True,
        blank=True
    )

    # Parts are one to many, reference to artifact included Part model.

    def __str__(self):
        return f"Artifact: {self.name or 'Unnamed'} (index={self.index})"
