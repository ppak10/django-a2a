from django.http import StreamingHttpResponse
from django_a2a.serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework import status
import json
import time

def message_stream(request):
    """
    Handles 'message/stream' RPC method and streams a response.
    """
    params = request.data.get("params")
    message = params.get("message")
    metadata = params.get("metadata")
    request_id = request.data.get("id", None)

    if not message:
        return Response({
            'jsonrpc': '2.0',
            "error": {
                "code": -32602,
                "message": "Missing 'message' in params."
            },
            'id': request_id
        }, status=status.HTTP_400_BAD_REQUEST)

    payload = {
        "history": [message],
        "metadata": metadata
    }

    serializer = TaskSerializer(data=payload)
    if not serializer.is_valid():
        return Response({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32602,
                'message': 'Invalid parameters.',
                'data': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # Save task
    user = request.user if request.user.is_authenticated else None
    serializer.save(created_by=user)
    result = serializer.data

    # Generator function to stream data
    def event_stream():
        try:
            # Send initial result
            yield f"data: {json.dumps({'status': 'started', 'result': result})}\n\n"
            time.sleep(1)

            # Simulate streaming steps (replace with actual logic)
            for i in range(1, 4):
                yield f"data: {json.dumps({'status': 'progress', 'step': i})}\n\n"
                time.sleep(1)

            yield f"data: {json.dumps({'status': 'complete'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response
