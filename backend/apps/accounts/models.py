from django.conf import settings
from django.db import models


class ApplicantProfile(models.Model):
    class TipoDocumento(models.TextChoices):
        DNI = "dni", "DNI"
        CARNE_EXTRANJERIA = "ce", "Carné de Extranjería"
        PASAPORTE = "pasaporte", "Pasaporte"

    class Sexo(models.TextChoices):
        MASCULINO = "m", "Masculino"
        FEMENINO = "f", "Femenino"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applicant_profile"
    )
    tipo_documento = models.CharField(max_length=10, choices=TipoDocumento.choices, blank=True)
    numero_documento = models.CharField(max_length=20, blank=True)
    nacionalidad = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=Sexo.choices, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    # Ubigeo: se guardan directo (no hay tabla propia, se resuelven desde una API externa cacheada)
    ubigeo_codigo = models.CharField(max_length=6, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_documento", "numero_documento"],
                condition=~models.Q(numero_documento=""),
                name="unique_tipo_numero_documento_non_blank",
            )
        ]

    def __str__(self):
        return f"Perfil de {self.user}"
