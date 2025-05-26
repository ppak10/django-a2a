from django.test import TestCase
from django.utils.timezone import now
from django_a2a.serializers import TaskStatusUpdateEventSerializer, TaskSerializer
from django_a2a.models import TaskStatus
import uuid

class TaskStatusUpdateEventSerializerTest(TestCase):

    def setUp(self):
        self.context_id = uuid.uuid4()

        # Use the TaskSerializer to create a Task
        task_data = {
            "contextId": str(self.context_id),
        }
        task_serializer = TaskSerializer(data=task_data)
        self.assertTrue(task_serializer.is_valid(), task_serializer.errors)
        self.task = task_serializer.save()

        self.timestamp = now().isoformat()

        self.valid_data = {
            "taskId": str(self.task.id),
            "contextId": str(self.context_id),
            "kind": "status-update",
            "status": {
                "state": TaskStatus.TaskState.WORKING,
                "timestamp": self.timestamp
            },
            "final": True,
            "metadata": {"step": "preprocessing", "attempt": 2}
        }

    def test_valid_data_passes(self):
        serializer = TaskStatusUpdateEventSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["final"], True)
        self.assertEqual(serializer.validated_data["metadata"]["step"], "preprocessing")

    def test_missing_optional_fields(self):
        minimal_data = {
            "taskId": str(self.task.id),
            "contextId": str(self.context_id),
            "kind": "status-update",
            "status": {
                "state": TaskStatus.TaskState.WORKING,
                "timestamp": now().isoformat()
            }
        }
        serializer = TaskStatusUpdateEventSerializer(data=minimal_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertFalse(serializer.validated_data.get("final", False))
        self.assertIsNone(serializer.validated_data.get("metadata"))

    def test_invalid_kind_fails(self):
        invalid_data = {**self.valid_data, "kind": "unknown-type"}
        serializer = TaskStatusUpdateEventSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("kind", serializer.errors)

    def test_missing_required_field_fails(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["taskId"]
        serializer = TaskStatusUpdateEventSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("taskId", serializer.errors)
