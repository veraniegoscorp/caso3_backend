from django import forms
from .models import contacto


class ContactoForm(forms.ModelForm):
    correo = forms.EmailField()

    class Meta:
        model = contacto
        fields = ['nombre', 'telefono', 'correo', 'direccion']