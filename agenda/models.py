from django.db import models
#nombre, teléfono, correo y dirección

class contacto(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.IntegerField(default=0)
    correo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
