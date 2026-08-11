# Resend — API Keys

Fuente: https://resend.com/docs/dashboard/api-keys/introduction

## Qué son

"API Keys are secret tokens used to authenticate your requests. Son únicos a la cuenta y deben mantenerse confidenciales" — mismo tratamiento que cualquier otro secreto del proyecto (nunca en chat, nunca commiteado; va en `.env`, gitignored, igual que `DEEPSEEK_API_KEY`/`DEEPGRAM_API_KEY`/`ELEVENLABS_API_KEY`).

Se pueden crear varios keys — sirve para separar por función/entorno (ej. uno para dev, otro para producción) y monitorear el uso de cada uno por separado.

## Crear y gestionar

Desde cuatro lugares:
- [Dashboard de API Keys](https://resend.com/api-keys)
- REST API de Resend
- CLI de Resend
- Servidor MCP de Resend

### Pasos desde el Dashboard

1. Ir a la página de API Keys.
2. Click en **Create API Key**.
3. Ponerle un nombre (máx. 50 caracteres) — acá usar `vacantia-dev`/`vacantia-prod` según el entorno (ver más abajo).
4. Elegir el **permiso**:
   - **"Sending access"**: solo puede mandar emails — es lo único que necesita nuestro backend Django (`send_mail`/`EmailMessage` vía `django-anymail`), así que es el permiso correcto para el key de esta app.
   - **"Full access"**: puede crear/borrar/leer/actualizar cualquier recurso de la cuenta (dominios, otros keys, etc.) — no hace falta para este proyecto, solo se usaría para automatizar la propia gestión de la cuenta de Resend, que no es nuestro caso.
5. (Opcional, solo si elegiste "Sending access") Restringir el key a un dominio específico — como el proyecto va a tener un solo dominio verificado (`vacantia.dev` o el subdominio que se use para email), conviene activarlo: si el key se filtra, no sirve para mandar desde otro dominio.

## Editar

Después de creado se puede modificar: nombre, nivel de permiso, dominio asociado.

**Importante:** no se puede volver a ver el valor del key después de creado — hay que guardarlo apenas se genera (en el `.env`, no en ningún otro lado, igual que el resto de los secretos del proyecto: `RESEND_API_KEY=re_xxxxxxxx`, con `.env` en `.gitignore`).

## Buenas prácticas

- Borrar keys inactivos por 30+ días.
- El dashboard muestra el conteo de requests por key — útil para detectar uso indebido o debuggear.
