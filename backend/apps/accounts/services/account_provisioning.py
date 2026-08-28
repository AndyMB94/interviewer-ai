import secrets
import string

from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.accounts.models import ApplicantProfile

POSTULANTE_GROUP_NAME = "Postulante"


def _generar_password_temporal(length=12):
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(length))


def provision_applicant_account(postulacion):
    """Crea la cuenta del postulante si no existe, o le resetea la contraseña si ya existía
    (de una postulación aprobada anterior) — así nunca depende de que recuerde una contraseña vieja.
    Devuelve (user, password_temporal, es_reset) -- es_reset es True cuando la cuenta ya existía
    de antes (Fase 10.3, para avisarle en el email que sus contraseñas previas ya no valen)."""
    group = Group.objects.get(name=POSTULANTE_GROUP_NAME)
    password_temporal = _generar_password_temporal()

    user, created = User.objects.get_or_create(
        username=postulacion.email,
        defaults={"email": postulacion.email},
    )
    user.set_password(password_temporal)
    user.save(update_fields=["password"])
    user.groups.add(group)

    ApplicantProfile.objects.get_or_create(user=user)

    return user, password_temporal, not created


def enviar_email_credenciales(postulacion, password_temporal, es_reset):
    html_content = render_to_string(
        "emails/credenciales_postulante.html",
        {
            "nombre": postulacion.nombre,
            "puesto": postulacion.puesto.titulo,
            "username": postulacion.email,
            "password_temporal": password_temporal,
            "fecha_limite_entrevista": postulacion.fecha_limite_entrevista.strftime("%d/%m/%Y"),
            "es_reset": es_reset,
        },
    )
    message = EmailMessage(
        subject=f"¡Su postulación a {postulacion.puesto.titulo} fue aprobada! — Vacantia",
        body=html_content,
        to=[postulacion.email],
    )
    message.content_subtype = "html"
    message.send()


def procesar_aprobacion(postulacion):
    user, password_temporal, es_reset = provision_applicant_account(postulacion)
    enviar_email_credenciales(postulacion, password_temporal, es_reset)
    return user
