from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone


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
    vacantes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="puestos", null=True, blank=True
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="puestos_creados"
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTO)
    # Fase 10.13: distinto de `vacantes` (cuántas personas se van a contratar) -- esto es cuántas
    # postulaciones como máximo se van a evaluar con el filtro de IA (control de costo/volumen).
    # El reclutador lo puede subir en cualquier momento; no hace falta "reabrir" el puesto aparte,
    # `acepta_postulaciones` se calcula al vuelo contra el valor actual.
    limite_postulaciones = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.titulo

    @property
    def acepta_postulaciones(self):
        return self.estado == self.Estado.ABIERTO and self.postulaciones.count() < self.limite_postulaciones


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
    # Fecha límite para completar la entrevista (aprobación + 3 días, Fase 10.1) -- null en
    # postulaciones sin aprobar y en las aprobadas antes de que existiera este campo.
    fecha_limite_entrevista = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["puesto", "email"], name="unique_puesto_email"),
        ]

    def __str__(self):
        return f"{self.nombre} → {self.puesto}"

    @property
    def entrevista_vencida(self):
        """Se calcula al vuelo contra la hora actual, sin ningún job en segundo plano que la
        marque -- mismo principio con el que ya expira el JWT en este proyecto (Fase 10.2)."""
        if self.fecha_limite_entrevista is None:
            return False
        return timezone.now() > self.fecha_limite_entrevista
