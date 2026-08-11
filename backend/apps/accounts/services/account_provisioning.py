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
    Devuelve (user, password_temporal)."""
    group = Group.objects.get(name=POSTULANTE_GROUP_NAME)
    password_temporal = _generar_password_temporal()

    user, _ = User.objects.get_or_create(
        username=postulacion.email,
        defaults={"email": postulacion.email},
    )
    user.set_password(password_temporal)
    user.save(update_fields=["password"])
    user.groups.add(group)

    ApplicantProfile.objects.get_or_create(user=user)

    return user, password_temporal


def enviar_email_credenciales(postulacion, password_temporal):
    html_content = render_to_string(
        "emails/credenciales_postulante.html",
        {
            "nombre": postulacion.nombre,
            "puesto": postulacion.puesto.titulo,
            "username": postulacion.email,
            "password_temporal": password_temporal,
        },
    )
    message = EmailMessage(
        subject=f"¡Tu postulación a {postulacion.puesto.titulo} fue aprobada! — Vacantia",
        body=html_content,
        to=[postulacion.email],
    )
    message.content_subtype = "html"
    message.send()


def procesar_aprobacion(postulacion):
    user, password_temporal = provision_applicant_account(postulacion)
    enviar_email_credenciales(postulacion, password_temporal)
    return user
