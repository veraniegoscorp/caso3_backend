from django.db import models
from django.core.exceptions import ValidationError
import re

class contacto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.IntegerField(default=0, verbose_name="Teléfono")
    correo = models.CharField(max_length=100, verbose_name="Correo Electrónico")
    direccion = models.CharField(max_length=100, verbose_name="Dirección")

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-id']

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    def clean(self):
        super().clean()
        # Validación y limpieza de Nombre
        if self.nombre:
            self.nombre = self.nombre.strip()
            if len(self.nombre) < 2:
                raise ValidationError({'nombre': 'El nombre debe tener al menos 2 caracteres.'})
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\'-]+$", self.nombre):
                raise ValidationError({'nombre': 'El nombre solo debe contener letras y espacios.'})

        # Validación de Teléfono
        if self.telefono is not None:
            if self.telefono <= 0:
                raise ValidationError({'telefono': 'El teléfono debe ser un número positivo.'})
            tel_str = str(self.telefono)
            if len(tel_str) < 7 or len(tel_str) > 15:
                raise ValidationError({'telefono': 'El teléfono debe tener entre 7 y 15 dígitos.'})

        # Validación de Correo
        if self.correo:
            self.correo = self.correo.strip().lower()
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, self.correo):
                raise ValidationError({'correo': 'Ingrese un formato de correo electrónico válido (ej: nombre@dominio.com).'})

        # Validación de Dirección
        if self.direccion:
            self.direccion = self.direccion.strip()
            if len(self.direccion) < 3:
                raise ValidationError({'direccion': 'La dirección debe tener al menos 3 caracteres.'})
