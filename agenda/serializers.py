from rest_framework import serializers

from .models import contacto

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacto
        fields = '__all__'