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
        task = Task.objects.create(contextId=uuid4())
        status = TaskStatus.objects.create(task=task, state=TaskStatus.TaskState.WORKING, timestamp=now())
        serializer = TaskStatusSerializer(status)
        data = serializer.data

        self.assertEqual(data["id"], status.id)
        self.assertEqual(data["task"], task.id)
        self.assertEqual(data["state"], TaskStatus.TaskState.WORKING)
        self.assertIsNotNone(data["timestamp"])


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(contextId=uuid4())

        # Attach a TaskStatus
        self.status = TaskStatus.objects.create(task=self.task, state=TaskStatus.TaskState.COMPLETED, timestamp=now())

        self.artifact = Artifact.objects.create(task=self.task)
        Part.objects.create(kind="text", text="artifact text", artifact=self.artifact)

        self.message = Message.objects.create(role="user")
        Part.objects.create(kind="text", text="message text", message=self.message)

        self.message.task = self.task  # Assuming reverse relation like `related_name="history"`
        self.message.save()

    def test_task_serializer_output(self):
        serializer = TaskSerializer(self.task)
        data = serializer.data

        self.assertEqual(data["id"], str(self.task.id))
        self.assertEqual(data["contextId"], str(self.task.contextId))
        
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
        contextId = uuid4()
        payload = {
            "contextId": str(contextId),
            "artifacts": [
                {
                    "parts": [
                        {"kind": "text", "text": "artifact 1 content"}
                    ]
                }
            ],
            "history": [
                {
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": "message 1 content"}
                    ]
                }
            ]
        }

        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()

        self.assertEqual(task.contextId, str(contextId))
        self.assertEqual(task.status.state, TaskStatus.TaskState.SUBMITTED)
        self.assertIsNotNone(task.status.timestamp)

        artifacts = Artifact.objects.filter(task=task)
        self.assertEqual(artifacts.count(), 1)
        self.assertEqual(artifacts[0].parts.first().text, "artifact 1 content")

        messages = Message.objects.filter(task=task)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].parts.first().text, "message 1 content")
        self.assertEqual(messages[0].role, "user")


    def test_create_task_with_client_generated_ids(self):
        id = uuid4()
        contextId = uuid4()
        payload = {
            "id": str(id),
            "contextId": str(contextId),
        }

        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()

        self.assertEqual(task.status.state, TaskStatus.TaskState.SUBMITTED)
        self.assertIsNotNone(task.status.timestamp)

        self.assertEqual(task.contextId, str(contextId))
        self.assertEqual(task.id, id)

    def test_create_task_with_duplicate_id(self):
        id = uuid4()
        contextId1 = uuid4()
        contextId2 = uuid4()

        # Create the initial task
        Task.objects.create(id=id, contextId=str(contextId1))

        # Attempt to create a second task with the same `id`
        payload = {
            "id": str(id),  # duplicate
            "contextId": str(contextId2),
        }

        serializer = TaskSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn('id', serializer.errors)

    def test_create_task_with_duplicate_contextId(self):
        id1 = uuid4()
        id2 = uuid4()
        contextId = uuid4()

        # Create the initial task
        Task.objects.create(id=id1, contextId=str(contextId))

        # Attempt to create a second task with the same `contextId`
        payload = {
            "id": str(id2),
            "contextId": str(contextId),  # duplicate
        }

        serializer = TaskSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
