from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response

from django_a2a.methods import message_send, message_stream

class MethodsView(APIView):
    permission_classes = []

    @classmethod
    def as_view(cls, **initkwargs):
        permissions = initkwargs.pop("permission_classes", None)
        view = super().as_view(**initkwargs)
        if permissions:
            view.cls.permission_classes = permissions
        return view
    
    def handle_exception(self, exc):
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed, PermissionDenied)):
            return Response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32600,
                    'message': 'Forbidden: Authentication or permission denied.'
                },
                'id': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        # fallback to DRF's default handler
        return super().handle_exception(exc)

    def is_valid_jsonrpc(self, data):
        return (
            isinstance(data, dict)
            and data.get("jsonrpc") == "2.0"
            and "method" in data
            and "id" in data
        )
    
    def method_not_found(self, data, not_implemented = False):
        message = f"Method not {'implemented yet.' if not_implemented else 'found.'}"
        return Response({
            'jsonrpc': '2.0',
            'error': {
                'code': -32601,
                'message': message
            },
            'id': data.get("id", None)
        }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if not self.is_valid_jsonrpc(request.data):
            return Response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32600,
                    'message': 'Invalid Request'
                },
                'id': request.data.get("id", None)
            }, status=status.HTTP_400_BAD_REQUEST)

        method = request.data.get("method")

        if method == 'message/send':
            return message_send(request)
        elif method == 'message/stream':
            return message_stream(request)
        elif method == 'tasks/get':
            return self.method_not_found(request.data, not_implemented=True)
        elif method == 'tasks/cancel':
            return self.method_not_found(request.data, not_implemented=True)
        elif method == 'tasks/pushNotificationConfig/set':
            return self.method_not_found(request.data, not_implemented=True)
        elif method == 'tasks/pushNotificationConfig/get':
            return self.method_not_found(request.data, not_implemented=True)
        elif method == 'tasks/resubscribe':
            return self.method_not_found(request.data, not_implemented=True)
        elif method == 'agent/authenticatedExtendedCard':
            return self.method_not_found(request.data, not_implemented=True)
        else:
            return self.method_not_found(request.data)
        
    def get(self, request, *args, **kwargs):
        return Response({
            'jsonrpc': '2.0',
            'error': {
                'code': -32601,
                'message': 'GET method is not supported. Use POST with a valid JSON-RPC method.'
            },
            'id': None
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
