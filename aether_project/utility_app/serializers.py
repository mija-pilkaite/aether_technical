from rest_framework import serializers
from .models import Project



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['address', 'kWh_consumption', 'escalator']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        project = Project.objects.create(user=user, **validated_data)
        return project