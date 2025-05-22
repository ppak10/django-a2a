from django.test import TestCase
from uuid import uuid4
from django.utils.timezone import now

from django_a2a.models.task import Task, TaskStatus
from django_a2a.models.message import Message
from django_a2a.models.part import Part
from django_a2a.models.artifact import Artifact
from django_a2a.serializers.task import TaskSerializer, TaskStatusSerializer


class TaskStatusSerializerTest(TestCase):
    def test_serialize_task_status(self):
        task = Task.objects.create(session_id=uuid4())
        status = TaskStatus.objects.create(task=task, state=TaskStatus.TaskState.WORKING, timestamp=now())
        serializer = TaskStatusSerializer(status)
        data = serializer.data

        self.assertEqual(data["id"], status.id)
        self.assertEqual(data["task"], task.id)
        self.assertEqual(data["state"], TaskStatus.TaskState.WORKING)
        self.assertIsNotNone(data["timestamp"])


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(session_id=uuid4())

        # Attach a TaskStatus
        self.status = TaskStatus.objects.create(task=self.task, state=TaskStatus.TaskState.COMPLETED, timestamp=now())

        self.artifact = Artifact.objects.create(task=self.task)
        Part.objects.create(type="text", text="artifact text", artifact=self.artifact)

        self.message = Message.objects.create(role="user")
        Part.objects.create(type="text", text="message text", message=self.message)

        self.message.task = self.task  # Assuming reverse relation like `related_name="history"`
        self.message.save()

    def test_task_serializer_output(self):
        serializer = TaskSerializer(self.task)
        data = serializer.data

        self.assertEqual(data["id"], str(self.task.id))
        self.assertEqual(data["session_id"], str(self.task.session_id))
        
        # Test nested status
        self.assertIn("status", data)
        self.assertEqual(data["status"]["state"], TaskStatus.TaskState.COMPLETED)

        # Test nested artifacts
        self.assertIn("artifacts", data)
        self.assertEqual(data["artifacts"][0]["parts"][0]["text"], "artifact text")

        # Test nested message history
        self.assertIn("history", data)
        self.assertEqual(data["history"][0]["parts"][0]["text"], "message text")

class TaskSerializerNestedWriteTest(TestCase):
    def test_create_task_with_artifacts_and_history(self):
        session_id = uuid4()
        payload = {
            "session_id": str(session_id),
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": "artifact 1 content"}
                    ]
                }
            ],
            "history": [
                {
                    "role": "user",
                    "parts": [
                        {"type": "text", "text": "message 1 content"}
                    ]
                }
            ]
        }

        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()

        self.assertEqual(task.session_id, session_id)

        artifacts = Artifact.objects.filter(task=task)
        self.assertEqual(artifacts.count(), 1)
        self.assertEqual(artifacts[0].parts.first().text, "artifact 1 content")

        messages = Message.objects.filter(task=task)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].parts.first().text, "message 1 content")
        self.assertEqual(messages[0].role, "user")