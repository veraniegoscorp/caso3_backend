from django import forms
from django.core.exceptions import ValidationError
from .models import contacto
import re

class ContactoForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control custom-input',
            'placeholder': 'Ej. Juan Pérez González',
            'autocomplete': 'name',
        }),
        error_messages={
            'required': 'El nombre completo es obligatorio.',
            'max_length': 'El nombre no puede superar los 100 caracteres.',
        }
    )

    telefono = forms.IntegerField(
        required=True,
        label="Número de Teléfono",
        min_value=1000000,
        max_value=999999999999999,
        widget=forms.NumberInput(attrs={
            'class': 'form-control custom-input',
            'placeholder': 'Ej. 987654321',
            'autocomplete': 'tel',
        }),
        error_messages={
            'required': 'El teléfono es obligatorio.',
            'invalid': 'Ingrese un número telefónico válido (solo números enteros).',
            'min_value': 'El teléfono debe tener al menos 7 dígitos.',
            'max_value': 'El teléfono no puede superar los 15 dígitos.',
        }
    )

    correo = forms.EmailField(
        max_length=100,
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control custom-input',
            'placeholder': 'Ej. juan.perez@email.com',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Por favor ingrese un correo con formato válido (ej: usuario@dominio.com).',
            'max_length': 'El correo no puede superar los 100 caracteres.',
        }
    )

    direccion = forms.CharField(
        max_length=100,
        required=True,
        label="Dirección",
        widget=forms.TextInput(attrs={
            'class': 'form-control custom-input',
            'placeholder': 'Ej. Av. Providencia 1234, Depto 402',
            'autocomplete': 'street-address',
        }),
        error_messages={
            'required': 'La dirección es obligatoria.',
            'max_length': 'La dirección no puede superar los 100 caracteres.',
        }
    )

    class Meta:
        model = contacto
        fields = ['nombre', 'telefono', 'correo', 'direccion']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre no puede estar vacío.')
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener un mínimo de 2 caracteres.')
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\'-]+$", nombre):
            raise ValidationError('El nombre solo debe contener letras, acentos y espacios.')
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono is None or telefono <= 0:
            raise ValidationError('Debe ingresar un número de teléfono positivo válido.')
        tel_str = str(telefono)
        if len(tel_str) < 7 or len(tel_str) > 15:
            raise ValidationError('El teléfono debe tener entre 7 y 15 dígitos.')
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        if not correo:
            raise ValidationError('El correo electrónico es requerido.')
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, correo):
            raise ValidationError('El correo electrónico debe tener una estructura válida (ej. usuario@dominio.com).')
        return correo

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion', '').strip()
        if not direccion:
            raise ValidationError('La dirección no puede estar vacía.')
        if len(direccion) < 3:
            raise ValidationError('La dirección debe tener al menos 3 caracteres.')
        return direccion