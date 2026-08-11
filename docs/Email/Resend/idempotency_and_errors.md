# Resend — Idempotencia y manejo de errores (relevante para Fase 9.4)

Fuente: https://resend.com/docs/ai-onboarding (sección "Quick Start Guides" — el resto de esa página es sobre conectar agentes de IA directo a la cuenta de Resend vía MCP/CLI, no aplica a este proyecto, donde Django le habla a la API vía `django-anymail`).

## Por qué importa acá

El envío de email de credenciales (Backend Fase 9.4) se dispara desde una tarea Celery cuando `screen_postulacion_task` (u otra tarea) decide `aprobado`. Si esa tarea falla después de mandar el email pero antes de terminar, y Celery la reintenta, sin protección se le mandaría el email de credenciales **dos veces** al mismo candidato.

## Idempotency keys

- Formato recomendado: `<tipo-de-evento>/<id-de-entidad>` — para nosotros algo como `credenciales-postulante/<postulacion_id>`.
- Expiran a las 24hs.
- Máximo 256 caracteres.
- Mismo payload con la misma key → Resend devuelve la respuesta original sin reenviar.
- Mismo key con payload distinto → error 409.

**Pendiente de confirmar al implementar:** si `django-anymail` expone este parámetro directamente (probablemente vía `message.esp_extra = {"idempotency_key": ...}`, patrón típico de anymail para pasar opciones específicas del proveedor) — hay que revisar la doc de `django-anymail` para Resend en el momento, no está confirmado en esta referencia.

## Manejo de errores

| Código   | Acción                                                      |
| -------- | ------------------------------------------------------------ |
| 400, 422 | Error de datos — corregir el request, no reintentar          |
| 401, 403 | API key inválido o dominio no verificado — no reintentar     |
| 409      | Conflicto de idempotency key — usar una key nueva o revisar el payload |
| 429      | Rate limit (10 req/s por defecto) — reintentar con backoff exponencial |
| 500      | Error del servidor de Resend — reintentar con backoff exponencial |

## Estrategia de reintento

Backoff exponencial (1s, 2s, 4s...), máximo 3-5 reintentos, **solo** para 429 y 500 — coincide con el patrón que Celery ya soporta nativo (`autoretry_for`, `retry_backoff`), no hace falta implementarlo a mano.
