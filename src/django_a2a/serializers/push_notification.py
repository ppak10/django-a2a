from rest_framework import serializers
    
class PushNotificationConfigSerializer(serializers.Serializer):
    # Define fields based on your actual push notification structure
    # For now, we assume an endpoint and a boolean flag
    endpoint = serializers.URLField()
    enabled = serializers.BooleanField()
