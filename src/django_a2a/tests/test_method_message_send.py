from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from django_a2a.views import MethodsView

# Subclass of MethodsView for authenticated testing
class CustomMethodsView(MethodsView):
    permission_classes = [IsAuthenticated]


User = get_user_model()

class MessageSendTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.valid_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "kind": "text",
                            "text": "Tell me a joke"
                        }
                    ]
                    # Optionally: "task_id": some_task_id
                },
                "metadata": {"context": "testing"}
            }
        }

        self.invalid_payload_missing_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "message/send",
            "params": {
                # "message" key is missing
                "metadata": {"context": "testing"}
            }
        }

    def test_message_send_success_authenticated(self):
        request = self.factory.post("/a2a/", self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        view = CustomMethodsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.data)
        self.assertEqual(response.data["jsonrpc"], "2.0")
        self.assertEqual(response.data["id"], 1)

        result = response.data["result"]
        for key in ["id", "contextId", "status", "artifacts", "history", "metadata"]:
            self.assertIn(key, result)

        self.assertEqual(
            result["history"][0]["parts"][0]["text"], "Tell me a joke"
        )
        self.assertEqual(response.data["result"]["status"]["state"], "submitted")

    def test_message_send_missing_message(self):
        request = self.factory.post("/a2a/", self.invalid_payload_missing_message, format='json')
        force_authenticate(request, user=self.user)
        view = CustomMethodsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["jsonrpc"], "2.0")
        self.assertEqual(response.data["id"], 2)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["code"], -32602)
        self.assertEqual(response.data["error"]["message"], "Missing 'message' in params.")
