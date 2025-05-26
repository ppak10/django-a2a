from django_a2a.serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework import status

def message_send(request):
    """
    Handles 'message/send' RPC method.
    """
    params = request.data.get("params")
    message = params.get("message")
    metadata = params.get("metadata")
    if not message:
        return Response({
            'jsonrpc': '2.0',
            "error": {
                "code": -32602,
                "message": "Missing 'message' in params."
            },
            'id': request.data.get("id", None)
        }, status=status.HTTP_400_BAD_REQUEST)

    payload = {
        # "artifacts": [] (Need to generate)
        "history": [message],
        "metadata": metadata
    }
    serializer = TaskSerializer(data=payload)
    if serializer.is_valid():
        # Handle Anonymous user
        user = request.user if request.user.is_authenticated else None
        serializer.save(created_by=user)

        result = serializer.data

        return Response({
            'jsonrpc': '2.0',
            'id': request.data.get("id"),
            'result': result,
        })
    
    return Response({
        'jsonrpc': '2.0',
        'id': request.data.get("id", None),
        'error': {
            'code': -32602,
            'message': 'Invalid parameters.',
            'data': serializer.errors  # 🔍 include details
        }
    }, status=status.HTTP_400_BAD_REQUEST)
