from rest_framework import serializers
from .models import TastePromptLog

class TastePromptLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TastePromptLog
        fields = ["id", "prompt", "response_json", "created_at"]