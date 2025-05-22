from base64 import b64encode
from django.core.exceptions import ValidationError
from django.test import TestCase
from a2a.models.part import FileContent, Part
from a2a.serializers.part import FileContentSerializer, PartSerializer


class FileContentSerializerTest(TestCase):

    def setUp(self):
        self.file_content = FileContent.objects.create(
            name="example.txt",
            mime_type="text/plain",
            bytes= b64encode(b"Hello, world!").decode('utf-8'),
            uri="http://example.com/file/example.txt"
        )

    def test_serialize_filecontent(self):
        serializer = FileContentSerializer(self.file_content)
        data = serializer.data
        self.assertEqual(data['name'], "example.txt")
        self.assertEqual(data['mime_type'], "text/plain")
        self.assertEqual(data['bytes'], self.file_content.bytes)
        self.assertEqual(data['uri'], "http://example.com/file/example.txt")

    def test_deserialize_filecontent(self):
        data = {
            "name": "newfile.txt",
            "mime_type": "text/plain",
            "bytes": b64encode(b"Hello, world!").decode('utf-8'),
            "uri": "http://example.com/file/newfile.txt"
        }
        serializer = FileContentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        file_content = serializer.save()
        self.assertEqual(file_content.name, "newfile.txt")
        self.assertEqual(file_content.mime_type, "text/plain")


class TextPartSerializerTest(TestCase):

    def setUp(self):
        self.part = Part.objects.create(
            type="text",
            metadata={"key": "value"},
            text="Sample text",
        )

    def test_serialize_part(self):
        serializer = PartSerializer(self.part)
        data = serializer.data
        self.assertEqual(data['type'], "text")
        self.assertEqual(data['metadata'], {"key": "value"})
        self.assertEqual(data['text'], "Sample text")

    def test_deserialize_part(self):
        # Usually, you don’t create nested relationships on create with read_only=True fields
        data = {
            "type": "text",
            "metadata": {"a": 1},
            "text": "New text",
        }
        serializer = PartSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        part = serializer.save()
        self.assertEqual(part.type, "text")
        self.assertEqual(part.metadata, {"a": 1})
        self.assertEqual(part.text, "New text")


class FilePartSerializerTest(TestCase):

    def setUp(self):
        self.file_content_serialize = FileContent.objects.create(
            name="example.txt",
            mime_type="text/plain",
            bytes=b"Hello, world!",
            uri="http://example.com/file/example.txt"
        )
        self.file_content_deserialize = FileContent.objects.create(
            name="example.txt",
            mime_type="text/plain",
            bytes=b"Hello, world!",
            uri="http://example.com/file/example.txt"
        )

        self.part = Part.objects.create(
            type="file",
            metadata={"key": "value"},
            file=self.file_content_serialize,
        )

    def test_serialize_part(self):
        serializer = PartSerializer(self.part)
        data = serializer.data
        self.assertEqual(data['type'], "file")
        self.assertEqual(data['metadata'], {"key": "value"})
        self.assertEqual(data['file']['id'], self.file_content_serialize.id)

    def test_deserialize_part(self):
        # Usually, you don’t create nested relationships on create with read_only=True fields
        data = {
            "type": "file",
            "file_id": self.file_content_deserialize.id,
            "metadata": {"a": 1},
        }
        serializer = PartSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        part = serializer.save()
        self.assertEqual(part.type, "file")
        self.assertEqual(part.metadata, {"a": 1})

class DataPartSerializerTest(TestCase):

    def setUp(self):
        self.part = Part.objects.create(
            type="data",
            metadata={"key": "value"},
            data={"foo": "bar"},
        )

    def test_serialize_part(self):
        serializer = PartSerializer(self.part)
        data = serializer.data
        self.assertEqual(data['type'], "data")
        self.assertEqual(data['metadata'], {"key": "value"})
        self.assertEqual(data['data'], {"foo": "bar"})

    def test_deserialize_part(self):
        # Usually, you don’t create nested relationships on create with read_only=True fields
        data = {
            "type": "data",
            "metadata": {"a": 1},
            "data": {"baz": "qux"},
        }
        serializer = PartSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        part = serializer.save()
        self.assertEqual(part.type, "data")
        self.assertEqual(part.metadata, {"a": 1})


class InvalidTypePartSerializerTest(TestCase):

    def setUp(self):
        self.file_content = FileContent.objects.create(
            name="example.txt",
            mime_type="text/plain",
            bytes=b"Hello, world!",
            uri="http://example.com/file/example.txt"
        )
        self.part = Part.objects.create(
            type="text",
            metadata={"key": "value"},
            text="Sample text",
        )

    def test_serialize_part(self):
        serializer = PartSerializer(self.part)
        data = serializer.data
        self.assertEqual(data['type'], "text")
        self.assertEqual(data['metadata'], {"key": "value"})
        self.assertEqual(data['text'], "Sample text")

    def test_deserialize_part_invalid_type(self):
        data = {
            "type": "text",
            "metadata": {"a": 1},
            "text": "New text",
            "data": {"baz": "qux"},  # Invalid because data is populated but type='text'
        }
        serializer = PartSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Validation at serializer level passes (if serializer doesn't call full_clean)
        
        # But calling save() triggers model clean -> ValidationError expected
        with self.assertRaises(ValidationError) as cm:
            serializer.save()
    
        # Optionally assert the message text:
        self.assertIn("Only `text` should be populated for type 'text'.", str(cm.exception))


