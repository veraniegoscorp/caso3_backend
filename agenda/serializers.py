from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import contacto

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = contacto
        fields = '__all__'

    def validate(self, attrs):
        instance = self.instance or self.Meta.model()
        for field, value in attrs.items():
            setattr(instance, field, value)

        try:
            instance.clean()
        except DjangoValidationError as error:
            detail = error.message_dict if hasattr(error, 'message_dict') else error.messages
            raise serializers.ValidationError(detail) from error

        for field in attrs:
            attrs[field] = getattr(instance, field)

        return attrs