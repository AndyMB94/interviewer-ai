from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Puesto(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        CERRADO = "cerrado", "Cerrado"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    requisitos = models.TextField()
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="puestos_creados"
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTO)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.titulo


class Postulacion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        RECHAZADO = "rechazado", "Rechazado"
        APROBADO = "aprobado", "Aprobado"

    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE, related_name="postulaciones")
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    cv = models.FileField(upload_to="cvs/", validators=[FileExtensionValidator(["pdf"])])
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    resultado_filtro = models.TextField(blank=True)  # razonamiento del filtro de IA, se llena en Fase 9.3
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nombre} → {self.puesto}"
