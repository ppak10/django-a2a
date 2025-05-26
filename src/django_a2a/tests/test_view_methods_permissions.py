from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model

from django_a2a.views import MethodsView


# Define a subclass of MethodsView with enforced permission_classes
class CustomMethodsView(MethodsView):
    permission_classes = [IsAuthenticated]


# Always use the dynamic user model to stay compatible with AUTH_USER_MODEL
User = get_user_model()

class MethodsPermissionsTestCase(APITestCase):
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
                    "parts": [{"kind": "text", "text": "tell me a joke"}],
                    "messageId": "some-id"
                },
                "metadata": {}
            }
        }

    def test_rejects_unauthenticated_user(self):
        request = self.factory.post("/a2a/", self.valid_payload, format='json')

        # Unauthenticated Request
        view = CustomMethodsView.as_view(permission_classes=[IsAuthenticated])
        response = view(request)

        # Print for debugging (optional)
        print("Response status code:", response.status_code)
        print("Response data:", response.data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('jsonrpc', response.data)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error']['message'], 'Forbidden: Authentication or permission denied.')

    def test_allows_authenticated_user(self):
        request = self.factory.post("/a2a/", self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        view = CustomMethodsView.as_view(permission_classes=[IsAuthenticated])
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_allows_unauthenticated_user(self):
        request = self.factory.post("/a2a/", self.valid_payload, format='json')

        # Unauthenticated Request
        view = CustomMethodsView.as_view(permission_classes=[AllowAny])
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_invalid_jsonrpc_payload(self):
        bad_payload = {"foo": "bar"}
        request = self.factory.post("/a2a/", bad_payload, format='json')
        force_authenticate(request, user=self.user)
        view = CustomMethodsView.as_view(permission_classes=[IsAuthenticated])
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], -32600)

    def test_method_not_found(self):
        invalid_method_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "nonexistent/method"
        }
        request = self.factory.post("/a2a/", invalid_method_payload, format='json')
        force_authenticate(request, user=self.user)
        view = CustomMethodsView.as_view(permission_classes=[IsAuthenticated])
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], -32601)
