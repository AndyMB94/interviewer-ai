from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class Puesto(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        CERRADO = "cerrado", "Cerrado"

    class Modalidad(models.TextChoices):
        PRESENCIAL = "presencial", "Presencial"
        REMOTO = "remoto", "Remoto"
        HIBRIDO = "hibrido", "Híbrido"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    funciones = models.TextField(blank=True)
    requisitos = models.TextField()
    requisitos_deseables = models.TextField(blank=True)
    modalidad = models.CharField(max_length=10, choices=Modalidad.choices, default=Modalidad.PRESENCIAL)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="puestos", null=True, blank=True
    )
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
