# Resend — Tipos de email (transactional vs. marketing)

Fuente: https://resend.com/docs/email-types

## Transactional (esto es lo que necesita Vacantia)

Mensaje disparado por una acción del usuario o un requisito legal, **1-a-1** (no masivo). Ejemplos que da la doc: confirmaciones de orden, reseteo de contraseña, notificaciones de cuenta — nuestro caso (mandar usuario/contraseña cuando se aprueba una `Postulacion`) encaja exactamente en esta categoría.

Se puede mandar desde: Resend API, Resend CLI, SMTP, servidor MCP, webhooks/automations. Para Django usamos la API vía `django-anymail` (ver `django_integration.md`).

## Marketing (no aplica a este proyecto)

Mensajes 1-a-muchos, regulados por leyes tipo CAN-SPAM/CASL (requieren opción de unsubscribe): newsletters, promociones, actualizaciones de producto. Se manejan con "Broadcasts" y necesitan un Plan de Marketing separado. **Vacantia no manda este tipo de email**, así que no hace falta ese plan.

## Planes

Resend separa el plan de Transactional del de Marketing — se puede tener solo el Transactional activo (que es lo que corresponde acá) y arrancar en el free tier, subiendo de tier según volumen si hace falta más adelante.
