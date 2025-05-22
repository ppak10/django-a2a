from django.test import TestCase

from django_a2a.models.message import Message
from django_a2a.models.part import Part
from django_a2a.models.task import Task

from django_a2a.serializers.message import MessageSerializer

class MessageSerializerTests(TestCase):
    def setUp(self):
        self.task = Task.objects.create()
        self.valid_data = {
            'role': 'user',
            'metadata': {},
            'task_id': self.task.id,
            'parts': [
                {
                    'type': 'text',
                    'text': 'This is a test part.'
                },
            ]
        }

    def test_message_serializer_valid_data(self):
        serializer = MessageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Part.objects.count(), 1)
        self.assertEqual(message.parts.first().text, 'This is a test part.')

    def test_message_serializer_no_parts(self):
        invalid_data = self.valid_data.copy()
        invalid_data['parts'] = []

        serializer = MessageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Message must contain at least one Part.', serializer.errors['non_field_errors'])
