# Resend — Integración con Django

Fuente: https://resend.com/docs/send-with-django

## Enfoque: `django-anymail`

La guía oficial usa el paquete [`django-anymail`](https://anymail.dev/), que reemplaza el `EMAIL_BACKEND` de Django para que `django.core.mail.send_mail`/`EmailMessage` (la API estándar de Django) hablen con Resend por debajo — no hay que aprender un SDK nuevo, se usa la API de envío de emails que Django ya trae.

## Instalación

```bash
pip install django-anymail[resend]
```

## Configuración (`settings.py`)

```python
INSTALLED_APPS = [
    # ...
    "anymail",
]

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY"),
}
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"  # cambiar por el dominio propio verificado en producción
```

## Envío simple

```python
from django.core.mail import send_mail

send_mail(
    subject="Hello from Django + Resend",
    message="Versión en texto plano.",
    from_email="Acme <onboarding@resend.dev>",
    recipient_list=["destinatario@example.com"],
    html_message="<strong>Funciona!</strong>",
)
```

## Envío con template (relevante para Backend Fase 9.4)

El caso de uso real del proyecto — mandar credenciales con un template en vez de texto plano:

```python
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

html_content = render_to_string('emails/credenciales.html', {
    'nombre': postulacion.nombre,
    'username': user.username,
    'password_temporal': password_generada,
    'login_url': 'https://vacantia.dev/login',
})
message = EmailMessage(
    subject="¡Tu postulación fue aprobada! — Vacantia",
    body=html_content,
    from_email="Vacantia <no-reply@vacantia.dev>",
    to=[postulacion.email],
)
message.content_subtype = "html"
message.send()
```

Esto se llamaría desde `screen_postulacion_task` (o una tarea Celery separada disparada cuando `decision == "aprobado"`), no desde la vista — mismo patrón que ya se usa para STT/LLM/TTS (trabajo pesado/con llamada externa va en Celery, no bloqueando el request).

## Ejemplos de referencia (repo oficial de Resend)

No hace falta para Fase 9.4 (con `send_mail`/`EmailMessage` alcanza), pero quedan anotados por si sirven más adelante:

- [Django app completa](https://github.com/resend/resend-examples/tree/main/python-resend-examples/django_app)
- [Envío con attachments](https://github.com/resend/resend-examples/blob/main/python-resend-examples/examples/with_attachments.py)
- [Envío programado (scheduled send)](https://github.com/resend/resend-examples/blob/main/python-resend-examples/examples/scheduled_send.py)
