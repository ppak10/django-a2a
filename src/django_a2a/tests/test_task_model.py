# tests/test_models.py

from django.test import TestCase
from uuid import UUID, uuid4

from a2a.models.task import Task, TaskStatus
from a2a.models.message import Message
from a2a.models.part import Part 
from django.utils.timezone import now


class TaskModelTest(TestCase):
    def test_create_task(self):
        task = Task.objects.create(session_id=uuid4(), metadata={"key": "value"})
        self.assertIsInstance(task.id, UUID)
        self.assertEqual(task.metadata["key"], "value")

    def test_str_representation(self):
        task = Task.objects.create(session_id=uuid4())
        self.assertIn(str(task.id), str(task))

    def test_ordering(self):
        Task.objects.create()
        Task.objects.create()
        tasks = Task.objects.all()
        self.assertLessEqual(tasks[0].id, tasks[1].id)


class TaskStatusModelTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(session_id=uuid4())
        self.message = Message.objects.create(role="user")
        self.part = Part.objects.create(type="text", text="Hello!", message=self.message)

    def test_create_status(self):
        status = TaskStatus.objects.create(
            task=self.task,
            state=TaskStatus.TaskState.SUBMITTED,
            timestamp=now(),
            message=self.message,
        )
        self.assertEqual(status.task, self.task)
        self.assertEqual(status.state, TaskStatus.TaskState.SUBMITTED)
        self.assertEqual(status.message.parts.first().text, "Hello!")

    def test_str_representation(self):
        status = TaskStatus.objects.create(
            task=self.task,
            state=TaskStatus.TaskState.COMPLETED,
        )
        self.assertIn("completed", str(status))

    def test_task_status_relationship(self):
        status = TaskStatus.objects.create(
            task=self.task,
            state=TaskStatus.TaskState.WORKING,
        )
        self.assertEqual(self.task.status, status)

    def test_soft_delete(self):
        status = TaskStatus.objects.create(
            task=self.task,
            state=TaskStatus.TaskState.FAILED,
        )
        status.delete()
        self.assertFalse(TaskStatus.objects.filter(id=status.id).exists())

