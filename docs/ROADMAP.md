# Roadmap

Fases de menor a mayor complejidad, subdivididas en pasos chicos. La regla: cada paso debe terminar en algo que se pueda correr y ver, antes de pasar al siguiente. Si un paso se siente "grande", se vuelve a partir.

## Backend (Django + Celery)

**Fase 0 — Setup base**
- [x] 0.1 Crear proyecto Django, correr el servidor vacío.
- [x] 0.2 Crear la app `interviews`, registrarla en settings.
- [x] 0.3 Endpoint REST `/api/health/` que devuelve `{"status": "ok"}`.
- [x] 0.4 Instalar pytest + pytest-django, configurar `pytest.ini` (o sección en `pyproject.toml`) apuntando a `config.settings`. Escribir el primer test: que un GET a `/api/health/` devuelva 200 y `{"status": "ok"}`.

**Fase 1 — LLM síncrono, sin audio, sin Celery**
- [x] 1.1 Instalar el SDK del LLM elegido y probar una llamada simple hardcodeada (un script suelto, sin vista todavía).
- [x] 1.2 Endpoint `/api/ask/` que recibe texto plano y devuelve la respuesta del LLM (todo síncrono, directo en la vista).
- [x] 1.3 Mover esa llamada a una función en `services/llm_service.py` (primer paso de orden, sin patrones todavía).

**Fase 2 — Async real con Celery**
- [x] 2.1 Instalar y configurar Celery + Redis; una tarea de prueba tipo "sumar dos números" para validar que la infraestructura funciona.
- [x] 2.2 Convertir la llamada al LLM en una tarea Celery; el endpoint dispara la tarea y responde con un `task_id`.
- [x] 2.3 Endpoint para consultar el resultado por `task_id` (polling simple, todavía sin Redis pub/sub ni WebSocket).

**Fase 3 — Speech-to-Text**
- [x] 3.1 Elegir proveedor (Deepgram / Whisper) y probar una transcripción de un audio de prueba en un script suelto, fuera de Django.
- [x] 3.2 Integrar esa llamada en una tarea Celery; endpoint que recibe un archivo de audio y devuelve el texto.

**Fase 4 — Text-to-Speech**
- [x] 4.1 Elegir proveedor (ElevenLabs u otro) y probar síntesis de un texto fijo en un script suelto.
- [x] 4.2 Integrar en una tarea Celery; endpoint que recibe texto y devuelve un archivo/URL de audio.

**Fase 5 — Puente hacia el gateway (Redis pub/sub)**
- [x] 5.1 Publicar un mensaje de prueba a un canal Redis desde un script Python, y consumirlo con otro script (validar el mecanismo antes de tocar Node).
- [x] 5.2 Cuando una tarea Celery (LLM/STT/TTS) termina, publicar el resultado al canal Redis de esa sesión.

**Fase 6 — Persistencia**
- [x] 6.1 Modelo `Interview` básico (usuario, fecha, estado).
- [x] 6.2 Modelos `Question` / `Answer` relacionados a la entrevista.
- [x] 6.3 Guardar cada intercambio (pregunta, transcripción, evaluación) en la base de datos.

**Fase 7 — Patrones (refactor, sin funcionalidad nueva)**
- [x] 7.1 Extraer interfaces `STTProvider`, `LLMProvider`, `TTSProvider` (Strategy) sin cambiar el comportamiento actual.
- [x] 7.2 Convertir cada llamada directa en un Adapter concreto de esas interfaces.
- [x] 7.3 Modelar `InterviewSession` como máquina de estados, validando transiciones.

## WS Gateway (Node + TypeScript + Express + Socket.io)

**Fase 0 — Setup base**
- [x] 0.1 Proyecto Node + Express corriendo, ruta `/health`.
- [x] 0.2 Instalar Socket.io; evento de conexión que solo loguea "cliente conectado".
- [x] 0.3 Evento de eco: el cliente manda texto, el servidor lo regresa igual.

**Fase 1 — Puente hacia Django (todavía con texto, no audio)**
- [x] 1.1 El gateway recibe un evento con texto y hace un POST al endpoint `/api/ask/` de Django (Backend Fase 1.2), devuelve la respuesta por el socket. _(Nota: implementado junto con 1.2 — para cuando se llegó acá, `/api/ask/` ya era la versión asíncrona de Backend Fase 2.2, la síncrona original de Fase 1.2 ya no existía.)_
- [x] 1.2 Cambiar esa llamada al endpoint asíncrono (Backend Fase 2.2): el gateway recibe un `task_id` y hace polling hasta tener el resultado.

**Fase 2 — Redis pub/sub real**
- [x] 2.1 El gateway se suscribe a Redis y loguea en consola los mensajes publicados (probar con el script de Backend Fase 5.1).
- [x] 2.2 Mapear `socket.id` a sesión de entrevista, y emitir al cliente correcto cuando llega un mensaje de su canal. _(Nota: no hizo falta un mapa explícito — el closure de JS en `interviewSocket.ts` ya asocia cada respuesta al socket correcto, ver DECISIONS.md/memoria del proyecto.)_

**Fase 3 — Audio real**
- [x] 3.1 Recibir audio binario del cliente por socket y reenviarlo como archivo al endpoint de Django (Backend Fase 3.2).
- [x] 3.2 Recibir el archivo/URL de audio de respuesta (TTS) y emitirlo al cliente.

**Fase 4 — Memoria de conversación** _(agregada 2026-07-30, no estaba prevista cuando se escribieron las fases anteriores — surge de Backend Fase 6, persistencia)_
- [x] 4.1 Rastrear el `interview_id` por conexión de socket (guardarlo la primera vez que `/api/ask/` lo devuelve) y mandarlo en cada pregunta/audio siguiente de esa misma conexión, para que el LLM tenga memoria continua durante toda la sesión de voz.

## Frontend (React + TypeScript)

**Fase 0 — Setup base**
- [x] 0.1 Proyecto React corriendo, pantalla en blanco con un texto.
- [x] 0.2 Instalar `socket.io-client`, conectar al gateway y mostrar "conectado" en consola.

**Fase 1 — Texto primero, sin audio**
- [x] 1.1 Input de texto + botón "enviar": manda el texto por socket y muestra la respuesta (contra Gateway Fase 1).

**Fase 2 — Captura de audio**
- [x] 2.1 Pedir permiso de micrófono (`getUserMedia`).
- [x] 2.2 Grabar audio con `MediaRecorder`, botón "grabar / detener".
- [x] 2.3 Enviar el audio grabado completo por socket al terminar de grabar (sin streaming en vivo todavía).

**Fase 3 — Reproducción**
- [x] 3.1 Recibir el audio de respuesta (TTS) del gateway y reproducirlo con un elemento `<audio>`.

**Fase 4 — UI de entrevista**
- [x] 4.1 Mostrar la pregunta actual.
- [x] 4.2 Mostrar transcripción en vivo cuando esté lista.
- [x] 4.3 Pantalla de feedback final.

## Infra / Deploy (Docker)

**Fase 0 — Infra mínima para desarrollo (desde el inicio)**
- [x] 0.1 `docker-compose.yml` que solo levante Postgres y Redis (el resto del código corre nativo: venv, pnpm).

**Fase 1 — Dockerizar cada servicio (cuando ya funcionen)**
- [x] 1.1 `Dockerfile` para `backend/` (Django + Celery worker).
- [x] 1.2 `Dockerfile` para `ws-gateway/` (Node).
- [x] 1.3 `Dockerfile` para `frontend/` (build de producción).
- [x] 1.4 Expandir `docker-compose.yml` para incluir los seis servicios (Postgres, Redis, backend, celery worker, ws-gateway, frontend) y probar que todo el flujo funciona igual que en nativo.

**Fase 2 — Despliegue**
- [x] 2.1 Elegir VPS (Contabo / Hostinger), instalar Docker ahí.
- [x] 2.2 Copiar `docker-compose.yml` + `.env` de producción al servidor, `docker compose up -d`.
- [x] 2.3 Nginx como reverse proxy + certificado SSL (Let's Encrypt / Certbot) delante de todo.
- [x] 2.4 Configurar logging de Django/Celery/Node a stdout (no a archivos), verificar que `docker compose logs <servicio>` muestre los mensajes correctamente.

**Fase 3 — Migrar el dominio a `vacantia.andymallcco.dev` (agregado 2026-08-17)**

**Contexto:** el producto se llama Vacantia desde el pivote (2026-08-06, ver DECISIONS.md), pero el dominio en producción sigue siendo `interviewer.andymallcco.dev` — quedó pendiente de aplicar. El dominio nuevo vive en el mismo VPS, mismo Nginx, mismos seis contenedores — no es una migración de infraestructura, es apuntar un dominio nuevo a lo que ya existe y avisarle a cada pieza (Django, el gateway, el frontend) cuál es su origen público.

**Decisión — convivencia con redirect, no corte abrupto:** `interviewer.andymallcco.dev` sigue funcionando durante la migración (agregado, no reemplazado, en `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS`/Nginx) hasta que todo esté verificado end-to-end en el dominio nuevo. Una vez confirmado, Nginx redirige el dominio viejo con un 301 permanente hacia el nuevo — así nadie con el link viejo (bookmarks, el propio README de portafolio en otros lados) se queda con un enlace roto, y queda claro cuál es el dominio "real" (buscadores y navegadores no se confunden con dos URLs sirviendo el mismo contenido).

**Dónde vive cada pieza del dominio (relevado antes de tocar nada):**
- **En el repo (código):** `backend/config/settings.py` — `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` tienen `interviewer.andymallcco.dev` hardcodeado.
- **Fuera del repo, solo en el VPS (no están en git):** un `.env` en la raíz del proyecto en el servidor con `PUBLIC_DJANGO_URL`/`CORS_ORIGINS` (los usa `ws-gateway`); un `frontend/.env` en el servidor con `VITE_API_URL`/`VITE_GATEWAY_URL` — estos se hornean **dentro del bundle de JS al momento del build** (Vite), no se leen en tiempo de ejecución, así que cualquier cambio ahí exige reconstruir el frontend después.
- **El Nginx del sistema** (no dockerizado, corre directo en el VPS, fuera del repo) — necesita un `server_name` nuevo y su propio certificado SSL.
- **El DNS en Porkbun** — hoy solo tiene el registro A de `interviewer.andymallcco.dev`.

- [x] 3.1 DNS (Porkbun): registro A `vacantia.andymallcco.dev` → `195.26.250.245` agregado. Esperando propagación antes de seguir con Certbot (3.2).
- [x] 3.2 Nginx + Certbot (en el VPS): `server_name`/`location` nuevos (mismo patrón que `interviewer.andymallcco.dev`: `/` → frontend 8080, `/socket.io/` → gateway 3000, `/media/` y `/api/` → backend 8000), certificado SSL emitido y desplegado con `certbot --nginx -d vacantia.andymallcco.dev`. `https://vacantia.andymallcco.dev` responde con HTTPS.
- [x] 3.3 Backend: `settings.py` — `vacantia.andymallcco.dev` agregado a `ALLOWED_HOSTS` y a `CORS_ALLOWED_ORIGINS`, sin borrar las entradas de `interviewer.andymallcco.dev` (conviven hasta 3.7). 105/105 tests pasando.
- [x] 3.4 VPS: `PUBLIC_DJANGO_URL=https://vacantia.andymallcco.dev` y `CORS_ORIGINS=https://interviewer.andymallcco.dev,https://vacantia.andymallcco.dev` (los dos orígenes conviven — `ws-gateway` los separa por coma) en el `.env` raíz del servidor. `ws-gateway` reiniciado.
- [x] 3.5 VPS: `VITE_API_URL`/`VITE_GATEWAY_URL` en `frontend/.env` del servidor actualizados a `https://vacantia.andymallcco.dev`, frontend reconstruido (`docker compose up -d --build frontend`).
- [x] 3.6 Verificación end-to-end completa en `https://vacantia.andymallcco.dev`, confirmada con capturas reales del navegador: postular con CV real → filtro de CV con IA (aprobó/rechazó correctamente según el caso) → cuenta creada automáticamente → email de credenciales llegado (Resend, `mail.andymallcco.dev`, no afectado por el cambio de dominio) → login → sala de espera personalizada → entrevista completa por texto **y por voz** (confirma que el WebSocket del gateway conecta bien contra el dominio nuevo, no solo HTTP) → panel de reclutador (puestos, postulaciones, detalle de la entrevista con transcripción y decisión). De paso se probó y confirmó el admin de Django en el dominio nuevo (ver los tres hallazgos arriba).
- [x] 3.7 Nginx — `interviewer.andymallcco.dev` ahora redirige (301 permanente, preservando la ruta: `/entrevista` → `/entrevista`, no solo la home) hacia `https://vacantia.andymallcco.dev` en vez de servir la app. Confirmado con `curl -w %{redirect_url}`. Las entradas viejas se dejan en `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS` — no molestan, y el redirect de Nginx nunca deja que una request llegue a Django por ese host de todas formas.
- [x] 3.8 Docs: `README.md` y `docs/ARCHITECTURE.md` actualizados con `vacantia.andymallcco.dev` como el dominio activo (nota de que el viejo redirige); nueva entrada en `docs/DECISIONS.md` (2026-08-17) documentando la migración y los tres hallazgos.

_Infra Fase 3 completa — `vacantia.andymallcco.dev` es el dominio de producción, `interviewer.andymallcco.dev` redirige (301) hacia él. Migración verificada end-to-end en el navegador._

**Fuera de alcance acá, explícitamente:** renombrar el repositorio de GitHub (`interviewer-ai` → algo con "vacantia") — es un cambio aparte, no depende de este ni bloquea nada del dominio, se evalúa después si hace falta.

**Hallazgo real, no relacionado con la migración en sí (encontrado en 3.2):** el Nginx de producción **nunca tuvo** un `location /admin/` — ni en `interviewer.andymallcco.dev` ni ahora en `vacantia.andymallcco.dev`. Sin ese bloque, `/admin/` caía en el `location /` (el frontend), que devolvía el `index.html` de la SPA con 200 — React Router mostraba su propia pantalla de "404 Not Found", no la de Django. El admin de Django nunca fue accesible por el dominio público en producción, solo en local. Se agregó `location /admin/ { proxy_pass http://127.0.0.1:8000; ... }` (mismo patrón que `/api/`) a los dos `server` blocks — confirmado con `curl` (302, redirect a `/admin/login/`, en vez de 200 con el HTML de la SPA) en ambos dominios.

**Segundo hallazgo, más serio (encontrado al abrir `/admin/` en el navegador — se veía sin ningún estilo):**
- `/static/admin/css/base.css` devolvía `text/html` (200) — mismo problema que con `/admin/`, faltaba `location /static/` en Nginx.
- Al investigar por qué el admin sirve sus estáticos "solo" sin ese `location`, se encontró la causa raíz: **`backend/config/settings.py` tiene `DEBUG = True` hardcodeado, sin override por variable de entorno** — producción corre con `DEBUG` activado. Esto no es solo por qué los estáticos se sirven así (`manage.py runserver` los sirve automático en modo `DEBUG`, algo que Django mismo advierte que no es apto para producción) — es una exposición real: cualquier error 500 en Django le muestra a cualquiera el stack trace completo, la config y variables de entorno.
- **Decisión:** se aplica un parche temporal ahora (agregar `location /static/` proxyeando a Django, igual que `/admin/`) para no bloquear la verificación de la migración de dominio (3.6), dejando explícitamente documentado que **no es la solución correcta** — se resuelve de fondo en la Fase 4 (abajo), que toca `DEBUG`, `collectstatic`, y reemplazar `runserver` por `gunicorn`.

**Tercer hallazgo (al intentar loguearse en el admin ya con estilos, tras el parche de `/static/`):** `Forbidden (403) — CSRF verification failed. Origin checking failed - https://vacantia.andymallcco.dev does not match any trusted origins.` Causa: `settings.py` nunca tuvo `CSRF_TRUSTED_ORIGINS` — desde Django 4.0, ese setting es obligatorio para aceptar POSTs por HTTPS con verificación de Origin (como el login del admin, que usa sesión + CSRF, a diferencia del resto de la API que es JWT puro). Mismo patrón que los dos hallazgos anteriores: el admin nunca se había probado de verdad por el dominio público, así que esto nunca hizo falta hasta ahora. Se agregó `CSRF_TRUSTED_ORIGINS = ["https://interviewer.andymallcco.dev", "https://vacantia.andymallcco.dev"]` a `settings.py` — a diferencia de los otros dos, este **sí es la solución final**, no un parche temporal (no depende de `DEBUG` ni de Nginx). 105/105 tests pasando. **Confirmado en el navegador:** login al admin en `https://vacantia.andymallcco.dev/admin/` funciona de punta a punta, con estilos correctos.

**Fase 4 — Hardening de producción (agregado 2026-08-17, completa):**
- [x] 4.1 `DEBUG = os.environ.get("DEBUG", "False") == "True"` en `settings.py` — `False` por default (seguro si falta la variable), `True` explícito en `backend/.env`/`.env.example` para local/dev. **Hallazgo real al revisar qué más asumía `DEBUG=True`:** `config/urls.py` tenía `if settings.DEBUG: urlpatterns += static(...)` para servir `/media/` — y el helper `static()` de Django además tiene su **propio** chequeo interno de `DEBUG` (se niega a registrar la URL aunque se saque el `if` de afuera). Con `DEBUG=False` en producción, `/media/` iba a devolver 404 pese a que Nginx ya lo proxya a Django. Se reemplazó por `path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT})` usando `django.views.static.serve` directo (sin pasar por el helper `static()`), documentado como decisión deliberada (no un shortcut) porque Nginx ya proxya `/media/` igual que `/api/`/`/admin/`/`/static/`, y el volumen de este proyecto no justifica un servidor de archivos aparte. 105/105 tests pasando.
- [x] 4.2 `STATIC_ROOT = BASE_DIR / "staticfiles"` en `settings.py`. `backend/Dockerfile` — `CMD` corre `collectstatic --noinput` antes de arrancar el servidor. `docker-compose.yml` — bind mount `./backend/staticfiles:/app/staticfiles` en el servicio `backend` (no `celery-worker`, no sirve HTTP) — a diferencia de `media_data` (volumen con nombre de Docker), acá hace falta un **bind mount a una carpeta real del host**, porque Nginx corre fuera de Docker y necesita una ruta de filesystem real para el `alias` de 4.3. `backend/staticfiles/` agregado a `.gitignore` (se regenera en cada arranque). Probado en Docker local: 157 archivos copiados (`admin` + `rest_framework`), visibles en `backend/staticfiles/` del host.
- [x] 4.3 Nginx: `location /static/` en `vacantia.andymallcco.dev` pasa de `proxy_pass` a `alias /srv/vacantia-static/` — sirve la carpeta de `collectstatic` directo, sin pasar por Django. **Decisión — carpeta fuera de `/root`, no `chmod o+x /root`:** el proyecto vive en `/root/interviewer-ai`, y `/root` es `drwx------` — `www-data` (usuario de Nginx) no puede ni entrar ahí. Se evaluó `chmod o+x /root` (rápido, un comando) contra bindear a una carpeta fuera de `/root` (ej. `/srv/vacantia-static/`, `755`) parametrizando la ruta en `docker-compose.yml` (`STATIC_HOST_PATH`, con default `./backend/staticfiles` para no romper local). Se eligió la segunda: aflojar `/root` es una decisión que se acumula — si el VPS aloja otro proyecto más adelante, esa apertura queda ahí afectando a cualquier cosa nueva bajo `/root`, no solo a este proyecto. La carpeta en `/srv` mantiene el radio de exposición acotado a un solo directorio pensado para esto. Confirmado en el navegador: admin con estilos correctos, servido por Nginx directo.
- [x] 4.4 `gunicorn==26.1.0` agregado a `requirements.txt` (`pip install` + `pip freeze`, mismo patrón que el resto de dependencias). `backend/Dockerfile` — `CMD` ahora corre `collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3` en vez de `manage.py runserver`. Probado en Docker local: arranca 3 workers, `GET /api/health/` responde 200.
- [x] 4.5 Verificación completa en producción, tras `git pull` + `docker compose up -d --build backend celery-worker` en la VPS: logs de arranque muestran `collectstatic` (157 archivos) y gunicorn con 3 workers escuchando en `0.0.0.0:8000`. `curl` confirmó `/admin/` → 302 (redirect a login, esperado sin sesión), `/static/admin/css/base.css` → 200 `text/css` servido por el `alias` de Nginx (no por Django), y una URL inexistente de la API devuelve la página 404 genérica de Django (sin stack trace ni config expuesta) — confirma `DEBUG=False` real en producción. Verificado en el navegador: admin con estilos correctos en `vacantia.andymallcco.dev`, y una entrevista de voz completa (audio, transcripción, "Entrevista finalizada") funcionando de punta a punta sin regresiones tras el cambio de servidor.

_Infra Fase 4 completa — producción corre con `DEBUG=False`, estáticos servidos por Nginx desde `/srv/vacantia-static` (collectstatic, sin pasar por Django), y gunicorn en vez de `runserver`._

**Fase 5 — Baja definitiva de `interviewer.andymallcco.dev` (agregado 2026-08-19):** tras confirmar que `vacantia.andymallcco.dev` funciona de punta a punta (Fase 3) y que el hardening de producción está completo (Fase 4), se decidió no mantener el dominio viejo ni como redirect — un solo dominio público, sin superficie extra que mantener (certificado, DNS, bloque de Nginx).
- [x] 5.1 Backend: `interviewer.andymallcco.dev` removido de `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS` en `settings.py` — queda solo `vacantia.andymallcco.dev`.
- [x] 5.2 VPS: `.env` raíz — `CORS_ORIGINS` actualizado a solo `https://vacantia.andymallcco.dev`, confirmado con `printenv` dentro del contenedor tras reiniciar `ws-gateway`.
- [x] 5.3 VPS: Nginx — `server` block de `interviewer.andymallcco.dev` eliminado de `sites-available`/`sites-enabled`, `nginx -t` exitoso, reload aplicado.
- [x] 5.4 VPS: `certbot delete --cert-name interviewer.andymallcco.dev` — certificado dado de baja.
- [x] 5.5 Porkbun: registro DNS (A) de `interviewer.andymallcco.dev` eliminado desde el panel web.
- [x] 5.6 Verificación: `curl -v https://interviewer.andymallcco.dev/` ya no llega al VPS — cae en el `CNAME *.andymallcco.dev → pixie.porkbun.com` (comodín de Porkbun para subdominios sin registro propio) y falla el handshake TLS (esa página de parking no tiene certificado para el hostname). `vacantia.andymallcco.dev` confirmado funcionando normal en el navegador tras el cambio.

_Infra Fase 5 completa — `vacantia.andymallcco.dev` es el único dominio público del proyecto; `interviewer.andymallcco.dev` fue dado de baja del todo (Nginx, certificado, DNS), sin dejar redirect._

## Mejoras post-lanzamiento (agregado 2026-08-05, no estaba previsto en el roadmap original)

- [x] P.1 Reescribir el system prompt del LLM en español neutro (sin voseo rioplatense).
- [x] P.2 Evaluar si el acento de la voz de ElevenLabs sigue sonando marcado después de P.1; si es así, probar otra voz de su librería. _(Nota: el acento ya sonaba neutro solo con P.1 — el cambio de voz que se hizo después fue por preferencia de género (voz femenina, "Gaby - Natura & Casual"), no por acento.)_
- [x] P.3 Rediseño visual del frontend (tipografía, layout tipo chat, estados de carga/grabación más claros), con Tailwind CSS + shadcn/ui (ver DECISIONS.md).
  - [x] P.3.1 Instalar y configurar Tailwind CSS (solo setup, confirmar que compila sin cambiar el diseño todavía).
  - [x] P.3.2 Instalar shadcn/ui, agregar un componente de prueba (Button) para confirmar que funciona.
  - [x] P.3.3 Separar `App.tsx` en componentes (`Header`, `QuestionDisplay`, `VoiceRecorder`, `TextAnswerForm`) con Tailwind, sin cambiar el diseño todavía (solo estructura).
  - [x] P.3.4 Aplicar el diseño real (layout tipo chat, colores, espaciado) usando shadcn/ui donde corresponda.
- [x] P.4 Terminar de cablear "Finalizar entrevista" (hallazgo del 2026-08-11: `Interview.status` nunca se seteaba a `finished` — quedó como dead code desde la Fase 6 original, y el botón no bloqueaba el chat después de "terminar"). Decisiones tomadas:
  - El postulante **no** ve una evaluación/feedback de la IA al finalizar — mismo criterio que el filtro de CVs (`resultado_filtro` de `Postulacion`, que tampoco se le muestra nunca al candidato). Cierre neutro para el candidato; la evaluación queda para el reclutador (Frontend Fase 6.3).
  - Quién decide cuándo termina: el candidato, con el botón (self-paced) — no se implementa cierre automático por IA ni por cantidad fija de preguntas; queda anotado como mejora futura posible, enganchada a `core/interview_session.py` (Fase 7.3, hoy standalone sin conectar al flujo real).
  - [x] P.4.1 Backend: `POST /api/interviews/<id>/finish/` marca `status=finished`.
  - [x] P.4.2 Gateway: evento de socket `finish` que llama a ese endpoint (usa el `interview_id` que el gateway ya trackea por conexión, no hace falta mandarlo desde el navegador).
  - [x] P.4.3 Frontend: al click en "Finalizar entrevista" — mensaje de cierre neutro (sin pedirle un resumen a la IA), dispara el evento `finish`, y bloquea el formulario de texto/voz y el propio botón. Probado end-to-end: chat se bloquea, `Interview.status` queda "Finalizada" en el admin.
- [x] P.5 Rediseño de las pantallas del candidato (agregado 2026-08-11, con el skill de shadcn/ui ya instalado — ver DECISIONS.md). Alcance: `/`, `/postular`, `/login`. **Sin sidebar acá** (sería sobreingeniería para pantallas de una sola tarea — el sidebar queda reservado para Frontend Fase 6, que sí tiene varias vistas).
  - [x] P.5.1 Navbar simple compartida entre las 3 pantallas (`RootLayout` + `Navbar`, layout route en `router.tsx`), con `DropdownMenu` de cuenta (avatar/email + "Cerrar sesión") cuando hay sesión activa — usa el endpoint `/api/auth/logout/` que ya existía desde Fase 8, solo faltaba conectarlo a la UI. `Header.tsx` (el `<h1>` viejo) se eliminó, reemplazado por la navbar. Probado end-to-end: navbar en las 3 pantallas, logout limpia la sesión de verdad (vuelve a pedir login).
  - [x] P.5.2 Mejorar los globos de chat en `QuestionDisplay` — avatar (`Avatar`/`AvatarFallback` de shadcn) con ícono de bot para Gaby y la inicial del email para el usuario, timestamp (`toLocaleTimeString`) debajo de cada mensaje, alineados con `items-start` (arriba, no abajo — se ve mejor con globos altos como los que tienen reproductor de audio).
  - [x] P.5.3 Pasada de responsive — verificado en Chrome DevTools (device toolbar, iPhone SE) en las 3 pantallas, sin superposiciones ni cortes. No hizo falta tocar código: los contenedores ya usaban `mx-auto max-w-*` + flex/grid sin anchos fijos en px, mobile-friendly desde el vamos.
- [x] P.6 Más pulido visual (agregado 2026-08-11, tras revisar qué faltaba después de P.5). Alcance:
  - [x] P.6.1 Toggle de tema claro/oscuro manual en la navbar (`useTheme` hook + ícono sol/luna). Sigue `prefers-color-scheme` del sistema por default; al elegir manualmente, se guarda en `localStorage` y se aplica clase `.light`/`.dark` en `<html>` (agregado también el override `:not(.light)` en `index.css` para forzar claro incluso con el sistema en oscuro, y un script inline en `index.html` que aplica la clase antes de que React monte, para evitar flash del tema incorrecto). Probado: cambia en el momento y persiste después de refrescar (F5).
  - [x] P.6.2 Loading skeleton en `/postular` mientras cargan los puestos (`PuestoCardSkeleton`, 4 placeholders con la misma forma que `PuestoCard`) en vez del texto plano "Cargando puestos...". Probado visualmente.
  - [x] P.6.3 Pulir visualmente `LoginPage` — card centrada verticalmente en la pantalla (antes quedaba pegada arriba), ícono `KeyRound` en un badge circular sobre el título, header centrado. Confirmado visualmente.
  - [x] P.6.4 Favicon propio — "V" blanca sobre fondo morado (`--primary`, mismo color de marca que el resto de la app), reemplaza el favicon default que había (era el logo de shadcn/base-ui, no propio). También se actualizó el `<title>` de `index.html` de "frontend" a "Vacantia".
- [x] P.7 Silent refresh de sesión al cargar la app (agregado 2026-08-12 — costo conocido desde el 2026-08-11, ver DECISIONS.md: el access token vive solo en memoria, se pierde al refrescar la página aunque la cookie del refresh token siga viva 7 días; se sintió más al usar login/dashboard de verdad en Frontend Fase 6).
  - [x] P.7.1 Backend: `CustomTokenObtainPairSerializer` agrega también `email` como claim del JWT (además de `groups`). Confirmado que el refresh (`/api/auth/token/refresh/`) preserva ambos claims automáticamente (simplejwt los copia del refresh token al access token nuevo), sin tocar `CookieTokenRefreshView`.
  - [x] P.7.2 Frontend: `lib/api.ts::refreshAccessToken()` — `POST /api/auth/token/refresh/` con `credentials: "include"`.
  - [x] P.7.3 Frontend: `AuthContext` intenta el refresh silencioso al montar la app; restaura `accessToken`/`userEmail`/`roles` si la cookie sigue viva, o se queda no logueado sin error si no. Estado `isCheckingSession` para que `RequireAuth` (y por extensión `RequireRole`) esperen antes de redirigir a `/login`. Probado end-to-end: login → F5 → sigue logueado, ya no vuelve a pedir credenciales.
- [x] P.8 Pulido de interacción (agregado 2026-08-13, tras revisar el producto ya completo funcionalmente — confirmaciones nativas del navegador, loaders de puro texto, hover inconsistente). Alcance: toda la app, candidato y reclutador por igual.
  - [x] P.8.1 Reemplazado `window.confirm` por `AlertDialog` de shadcn (instalado con `npx shadcn@latest add alert-dialog`) en los dos lugares donde se usaba: `InterviewPage.tsx` (bloqueo de salida de una entrevista activa, controlado por `blocker.state === "blocked"`) e `InterviewDetailPage.tsx` (confirmar avanza/no avanza, estado `pendingDecision` abre el diálogo con el mensaje correspondiente). Probado end-to-end en el navegador en ambos lugares.
  - [x] P.8.2 `Skeleton` en vez de texto "Cargando..." — `PuestosPage.tsx`, `PostulacionesPage.tsx` (filas de tabla), `PuestoDetailPage.tsx`, `InterviewDetailPage.tsx` (forma de card). Probado con throttling de red simulado (3G en Chrome DevTools) para poder verlo — en local, sin throttling, la carga es demasiado rápida para notarlo a simple vista.
  - [x] P.8.3 `Spinner` de shadcn (instalado con `npx shadcn@latest add spinner`) en botones con acción en curso — enviar postulación (`PuestoDetailPage`), avanza/no avanza (`InterviewDetailPage`), login (`LoginPage`, ver P.8.5). Mismo patrón: `data-icon="inline-start"` + `disabled`, nunca un prop `isLoading` propio del `Button`.
  - [x] P.8.4 Hover/transición — revisado y **no hizo falta agregar nada**: `TableRow` de shadcn ya trae `hover:bg-muted/50` incorporado de fábrica, y cada variante de `Button` ya tiene sus propios estados hover. Las cards informativas de `PuestoDetailPage`/`InterviewDetailPage` (Resultado del filtro, Decisión, Transcripción) deliberadamente **no** llevan hover — no son clickeables, y agregarles `hover:shadow-lg` sería un affordance engañoso (daría a entender que se puede interactuar con ellas). Solo `PuestoCard` lo tiene, porque es la única que realmente es un link.
  - [x] P.8.5 `LoginPage` — transición de entrada sutil (`animate-in fade-in-0 slide-in-from-bottom-2 duration-300` en la `Card`) y `Spinner` en el botón de submit mientras autentica, mismo patrón que P.8.3.
  - [x] P.8.6 Verificación visual completa en el navegador: login (fade-in + spinner, confirmado con throttling 3G porque local es demasiado rápido para notarlo a ojo), skeletons del dashboard (confirmado con 3G), `AlertDialog` de decisión avanza/no avanza, y `AlertDialog` de bloqueo de salida de entrevista activa — los cuatro confirmados funcionando con capturas de pantalla reales, no solo revisión de código.
- [x] P.9 Logo de la navbar consciente del rol (agregado 2026-08-13, encontrado al revisar si un Postulante logueado puede volver a `/entrevista` después de navegar afuera). `Navbar.tsx` linkeaba el logo "Vacantia" siempre a `/` (la grilla pública) sin importar el rol — dos problemas reales, no cosméticos:
  - Un **Postulante** que navega afuera de `/entrevista` (antes de empezar, o después de terminar — el bloqueo de P.8.1/Frontend 7.3 solo cubre mientras la entrevista está activa sin terminar) no tenía forma de volver salvo escribiendo la URL a mano; el dropdown de cuenta solo tiene el email y "Cerrar sesión".
  - Un **Reclutador** que hacía click en el logo salía de su panel hacia la grilla pública de postulantes — no tiene sentido para alguien logueado con ese rol, debería volver a `/dashboard`.
  - [x] P.9.1 `Navbar.tsx` — el logo linkea según el rol: sin sesión → `/`, `roles.includes("Postulante")` → `/entrevista`, `roles.includes("Reclutador")` → `/dashboard`. Usa `roles` que `AuthContext` ya expone (mismo criterio que el redirect post-login en `LoginPage.tsx`).
  - [x] P.9.2 Probado end-to-end en el navegador: logueado como reclutador el logo lleva a `/dashboard`; logueado como postulante lleva a `/entrevista`.
- [x] P.10 Composer unificado para la entrevista (agregado 2026-08-13, tras revisar el panel de chat del candidato). Antes `TextAnswerForm.tsx` y `VoiceRecorder.tsx` eran dos `Card` separadas apiladas debajo del chat, cada una con su propio título ("Responder por texto" / "Responder por voz") — se veía como dos formularios pegados, no como un chat real. Los chats reales (WhatsApp, ChatGPT, Messenger) tienen un solo "composer": input de texto + ícono de mic + botón de enviar, todos en la misma fila, sin títulos de sección.
  - **Componente nuevo `MessageComposer.tsx`**, reemplaza a `TextAnswerForm.tsx` y `VoiceRecorder.tsx` (borrados). Usa `InputGroup`/`InputGroupInput`/`InputGroupAddon` (`align="inline-end"`)/`InputGroupButton` de shadcn (instalado con `npx shadcn@latest add input-group`).
  - **Un solo botón de mic con 3 estados visuales** (ícono `Mic`/`Square` de lucide, cambia según el estado):
    1. Sin permiso todavía: ícono `Mic`, el click llama a `requestPermission()` (sin cambios en `useMicrophone`).
    2. Permiso concedido, sin grabar: mismo ícono `Mic`, el click arranca a grabar directo (`startRecording()`) — un click menos que antes, que exigía ver "Micrófono habilitado" y después apretar un botón "Grabar" aparte.
    3. Grabando: ícono `Square` (parar), `variant="destructive"`, con el punto pulsante "Grabando..." al lado.
  - **Errores de micrófono** se muestran como texto chico debajo del composer (`text-destructive`, ícono `CircleAlert`), no en una card aparte.
  - Botón de enviar (texto) sigue mandando con Enter o click, ahora dentro del `InputGroupAddon` en vez de un `Button` suelto al lado del `Input`.
  - `InterviewPage.tsx` — reemplazó el bloque `<TextAnswerForm />` + `<VoiceRecorder />` por `<MessageComposer />`, mismas props que ya recibían ambos (`useMicrophone`/`useSocket` sin cambios, fue puramente de presentación).
  - **Probado end-to-end con micrófono real** (no solo revisión de código): mensaje de texto enviado y respondido correctamente; grabación de voz con el flujo nuevo de menos clicks (permiso → click directo arranca a grabar → click para parar) transcrita correctamente y respondida por Gaby con audio — confirmado en el navegador, no solo revisión de código.
- [x] P.11 Título "Feedback final" era inconsistente con la decisión de producto ya tomada (encontrado 2026-08-13, probando P.10 en el navegador). `QuestionDisplay.tsx` ponía `"Feedback final"` como título de la card al terminar la entrevista — pero el contenido mostrado ahí es solo el mensaje neutro "Gracias por su tiempo...", **sin ningún feedback real**. Contradecía la decisión ya tomada en Fase P.4 (ver DECISIONS.md): el candidato nunca ve una evaluación de la IA, ni al finalizar, igual que nunca ve el `resultado_filtro` del CV.
  - [x] P.11.1 Título cambiado a `"Entrevista finalizada"`, consistente con "el candidato nunca ve evaluación".
  - [x] P.11.2 Confirmado visualmente en el navegador: al finalizar una entrevista, el título dice "Entrevista finalizada".
- [ ] P.12 Manejo de errores, confirmaciones y campos obligatorios (agregado 2026-08-25, encontrado al auditar el frontend tras el CRUD de puestos de 9.11). Alcance: toda la app, no solo el dashboard.

**Contexto:** al revisar qué faltaba de pulido después de construir el CRUD de puestos (9.11), aparecieron tres problemas reales, uno de ellos un bug funcional, no solo estética:
1. **Bug real:** `PuestosPage.tsx::cambiarEstado` (usada por "Cerrar puesto"/"Reabrir puesto") no tiene ningún `try/catch` — si el `PATCH` falla, la promesa rechaza sin que nadie la atrape: nada se muestra, el botón no se libera, no hay señal de error. Es el único punto de la app que actualiza algo sin manejar el error.
2. **Sin sistema de notificaciones:** no hay ningún componente de toast instalado. Crear/editar un puesto redirige al dashboard, cerrar/reabrir cambia el badge — pero no hay una confirmación explícita ("Puesto creado", "Puesto cerrado", etc.) en ningún lado, y un error (aparte del de guardar el formulario, que sí se muestra inline) no tiene dónde aparecer.
3. **Campos obligatorios sin marca visual:** `required` está puesto como atributo HTML en 9 campos entre 3 formularios (`PuestoFormPage`, el formulario de postulación de `PuestoDetailPage`, `LoginPage`), pero ningún `Label` lo indica — recién se entera al enviar y toparse con la validación nativa del navegador.

**Decisión 1 — `toast` de shadcn (Base UI), no `sonner`:** el proyecto usa el `base` de shadcn (Base UI), no Radix — `sonner` es la opción recomendada para proyectos Radix/React Aria, mientras que shadcn tiene un componente `toast` propio pensado para Base UI. Se usa ese, ya que mezclar primitivas de dos ecosistemas distintos (Base UI en todo el resto de la app, Radix solo para el toast) sería inconsistente sin necesidad.

**Decisión 2 — el toast cubre confirmaciones y errores que hoy no tienen dónde mostrarse, no reemplaza lo que ya funciona:** los errores de formulario (`PuestoFormPage`, `PuestoDetailPage`, `LoginPage`) ya se muestran inline junto al campo/botón correspondiente — eso se queda como está, es más preciso que un toast genérico para saber qué falló. El toast se usa donde hoy no hay ninguna señal: crear/editar/cerrar/reabrir un puesto (éxito), y el error de red de `cambiarEstado` (punto 1 de arriba, que hoy no se ve en ningún lado).

**Decisión 3 — asterisco en el `Label` compartido, no repetir el marcado a mano en cada campo:** se agrega un prop `required` opcional a `components/ui/label.tsx` (agrega un `<span>` con el asterisco en rojo) — un solo cambio en el componente compartido, en vez de escribir `Título *` a mano en 9 lugares distintos.

- [x] P.12.1 Instalado `toast` de shadcn (`npx shadcn@latest add toast`) — es un `ToastManager` de Base UI (`createToastManager()`), no un hook: se importa el objeto `toast` ya creado desde `components/ui/toast.tsx` y se llama `toast.add({ title, type })` desde cualquier lado, sin Provider por componente. `<Toaster>` montado una sola vez en `main.tsx`, envolviendo `AuthProvider`+`RouterProvider`, para que sobreviva a la navegación entre rutas.
- [x] P.12.2 `PuestosPage.tsx::cambiarEstado` — `try/catch` real, `actualizandoId` (el id del puesto en curso) deshabilita el botón clickeado y muestra `Spinner` mientras la request está en vuelo, `toast.add({type: "error", ...})` si `updatePuesto` falla.
- [x] P.12.3 Toast de éxito al crear/editar (`PuestoFormPage.tsx`, antes de `navigate("/dashboard")`) y al cerrar/reabrir un puesto (`PuestosPage.tsx`, dentro de `cambiarEstado`).
- [x] P.12.4 `components/ui/label.tsx` — prop `required?: boolean`, agrega un asterisco (`<span className="text-destructive">*</span>`) al final del label cuando está presente. Aplicado a los 9 campos `required` existentes: `titulo`/`descripcion`/`requisitos`/`vacantes` (`PuestoFormPage.tsx`), `nombre`/`email`/`cv` (`PuestoDetailPage.tsx`), `email`/`password` (`LoginPage.tsx`).
- [x] P.12.5 Verificado en el navegador: crear/editar/cerrar/reabrir un puesto muestra su toast de éxito correspondiente, el spinner aparece en el botón de cerrar/reabrir mientras la request está en curso, y el asterisco se ve en los campos obligatorios.

_P.12 completo — toasts de éxito/error donde antes no había ninguna señal, el bug de `cambiarEstado` sin manejo de errores quedó arreglado, y los campos obligatorios están marcados visualmente._

- [x] P.13 Hallazgo casual (2026-08-25, revisando P.12 en el navegador): el `DropdownMenu` de cuenta en `Navbar.tsx` no mostraba el email completo — Base UI hereda el ancho del popup del trigger (`w-(--anchor-width)`), y el trigger acá es el avatar circular chico, así que el `min-w-32` (128px) del componente compartido no alcanzaba para un email real. Mismo problema de fondo que ya se había resuelto en el `Select` de categorías de `ApplyPage` (Fase 9.9). Arreglado con `className="w-64"` en el `DropdownMenuContent` de `Navbar.tsx` (fix puntual, no se tocó el componente compartido — es el único lugar del proyecto que usa `DropdownMenu`) + `truncate` en el `DropdownMenuLabel` del email como resguardo para uno todavía más largo. Confirmado visualmente en el navegador.
- [ ] P.14 Footer, navbar, transiciones y efectos visuales (agregado 2026-08-25, encontrado al revisar el pulido visual general — el candidato lo pidió explícitamente: "mejorar footer, navbar... transiciones, loaders, efectos del mouse"). Alcance: páginas públicas + login, sin tocar el dashboard.

**Contexto:** `RootLayout.tsx` es hoy literalmente `<Navbar /><Outlet />` — no hay ningún footer en toda la app, ni en `ApplyPage` ni en ninguna otra pantalla. Como el proyecto es explícitamente de portafolio (ver README, "Por qué este proyecto"), no tener un link al repo en ningún lado es una pérdida real: alguien que llega a la demo no tiene forma de encontrar el código. Los otros puntos pedidos (fondo del login, transiciones, hover) son de pulido visual, no huecos funcionales — se evalúa cada uno con honestidad en vez de agregar decoración porque sí.

**Decisión 1 — el footer va en un layout público nuevo, no en `RootLayout` directo:** `RootLayout` envuelve *todas* las rutas, incluido `/dashboard` (que después anida su propio `DashboardLayout` con sidebar) — meter el footer ahí lo mostraría también debajo del panel del reclutador, compitiendo con la sidebar sin aportar nada (el reclutador ya está "adentro" del producto, no navegando el portafolio). Se crea `PublicLayout.tsx` (mismo patrón que ya existe para `DashboardLayout`: un layout anidado para un subconjunto de rutas), con `<Outlet /><Footer />`, usado solo en `/`, `/puestos/:id` y `/login` — no en `/entrevista`, `/perfil` ni `/dashboard/*`.

**Decisión 2 — el footer es informativo, no un menú de sitio:** un solo bloque simple con link al repo de GitHub (`github.com/AndyMB94/interviewer-ai`, el que ya usa el proyecto) y una línea corta ("Proyecto de portafolio — Andy Mallcco" o similar) — no se inventan secciones de "Sobre nosotros"/"Contacto"/redes que no existen todavía, sería relleno.

**Decisión 3 — no hay carrusel: no hay contenido real para rotar.** Un carrusel necesita algo que tenga sentido mostrando varios ítems en rotación (testimonios, banners de puestos destacados) — hoy no existe ese concepto en el producto, y forzar uno vacío (o con los mismos puestos que ya se ven en la grilla) sería decoración sin sustancia. En su lugar: un tratamiento visual sutil (gradiente/blur con el color de marca, `bg-primary/10` ya se usa en el ícono del login) detrás de la card de `LoginPage` — mismo espíritu, sin inventar contenido que no existe.

**Decisión 4 — transiciones: extender el patrón que ya existe, no traer una librería nueva.** `LoginPage` ya usa `animate-in fade-in-0 slide-in-from-bottom-2` (P.6/P.8.5) — Tailwind puro, sin dependencia nueva. Se aplica el mismo patrón a `ApplyPage`, `PuestoDetailPage` y las páginas del dashboard, y se le suma un stagger simple (delay incremental por índice) a las cards de la grilla de `ApplyPage`, para que entren una después de otra en vez de todas a la vez.

**Decisión 5 — hover: revisar, no dar por hecho que falta.** `PuestoCard.tsx` ya tiene `transition-shadow hover:shadow-lg` (evaluado a fondo en P.8.4, que decidió a propósito no agregar hover a elementos no clickeables). Se evalúa si sumar un `hover:border-primary/50` sutil a `PuestoCard` únicamente — no se toca nada más, para no repetir el trabajo que P.8.4 ya hizo bien.

**Hallazgo al revisar `PuestoCard.tsx` para esto:** tiene su propio `MODALIDAD_LABEL` duplicado — no usa el compartido `lib/puesto.ts` que se creó en 6.7.1 (esa extracción se hizo pensando en `PuestoDetailPage`/`PuestoFormPage`/`PuestoDetailSheet`, y se pasó por alto `PuestoCard`). Se corrige de paso.

- [x] P.14.1 `components/Footer.tsx` — link al repo de GitHub (ícono `Code2` de `lucide-react`, ya que la librería no incluye logos de marcas como GitHub desde hace tiempo) + línea de portafolio (Decisión 2).
- [x] P.14.2 `components/PublicLayout.tsx` — `<Outlet /><Footer />`, anidado dentro de `RootLayout` en `router.tsx` solo para `/`, `/puestos/:id`, `/login` (Decisión 1).
- [x] P.14.3 `Navbar.tsx` — `sticky top-0 z-40` + `bg-background/80 backdrop-blur supports-backdrop-filter:bg-background/60` (toque sutil, no rediseño).
- [x] P.14.4 `LoginPage.tsx` — círculo `bg-primary/20 blur-3xl` posicionado detrás de la `Card` (`absolute`, `pointer-events-none`, `aria-hidden`), contenedor con `overflow-hidden` para que no genere scroll horizontal (Decisión 3).
- [x] P.14.5 Transiciones de entrada (`animate-in fade-in-0 slide-in-from-bottom-2 duration-300`) agregadas a `ApplyPage.tsx`, `PuestoDetailPage.tsx`, `PuestosPage.tsx`, `PostulacionesPage.tsx`, `InterviewDetailPage.tsx` y `PuestoFormPage.tsx`; stagger por índice (`animationDelay: ${index * 50}ms`, con `fill-mode-both` para que no haya flash antes del delay) en las cards de `ApplyPage` (Decisión 4).
- [x] P.14.6 `PuestoCard.tsx` — sumado `hover:border-primary/50` a la transición de sombra que ya tenía; corregido el `MODALIDAD_LABEL` duplicado para que importe el compartido de `lib/puesto.ts` (hallazgo, ver arriba) en vez de tener su propia copia.
- [x] P.14.7 Verificación en el navegador. **Hallazgo real durante la verificación:** en páginas de contenido corto (ej. `/puestos/:id`), el footer no quedaba pegado abajo del todo del viewport — flotaba justo debajo del contenido, dejando un espacio en blanco entre el footer y el borde inferior de la pantalla. Causa: `PublicLayout.tsx` no tenía el layout flex necesario para el patrón "sticky footer" (contenido con `flex-1` empujando el footer hacia abajo). Arreglado en `RootLayout.tsx` (`flex min-h-screen flex-col`, el contenedor del `Outlet` como `flex flex-1 flex-col`) y `PublicLayout.tsx` (su propio contenido en `flex-1`, footer fuera de ese `flex-1`). Confirmado que `/dashboard` (que usa `Sidebar`, sensible al alto del contenedor) no se rompió con el cambio. De paso, el texto del footer pasó de "Vacantia — proyecto de portafolio, Andy Mallcco." a **"Desarrollado por Andy Mallcco"** — más profesional, sin sonar contradictorio al lado de un link a "Todos los derechos reservados" cuando el código es público en GitHub. Resto verificado: footer visible en `/`, `/puestos/:id`, `/login`, ausente en `/entrevista`/`/perfil`/`/dashboard`; navbar con blur al scrollear; login con el detalle de fondo; entrada animada de las cards en `/`; hover del `PuestoCard`.

_Frontend P.14 completo — footer (con el patrón sticky-footer correcto), navbar con blur, detalle de fondo en el login, transiciones de entrada, y hover mejorado en `PuestoCard`._

_Pendiente aparte, explícitamente de más baja prioridad y para después de P.14: limpiar los puestos de prueba creados durante las pruebas manuales de esta sesión ("fefef 😀 ef 😀", "sd", "Puesto de prueba CRUD 1", etc.) antes de considerar la demo presentable._

## Pivote: plataforma de reclutamiento con IA (agregado 2026-08-06, reemplaza la sección "Autenticación" anterior)

**Contexto:** el proyecto deja de ser solo una herramienta de práctica de entrevistas y pasa a ser un embudo de reclutamiento completo: una empresa publica un puesto, los candidatos postulan mandando su CV (sin cuenta todavía), un filtro con IA evalúa el fit contra el puesto, y **solo si aprueba** se le crea una cuenta automáticamente y se le mandan las credenciales por correo — recién ahí hace la entrevista de voz con la IA. Un reclutador tiene su propio panel para ver los postulantes de sus puestos y los resultados de sus entrevistas. Ver `docs/DECISIONS.md` para el detalle de cada decisión tomada acá.

**Nombre del proyecto:** se decidió renombrar a **Vacantia**. Aplicado en README/docs desde entonces, y en el dominio de producción desde Infra Fase 3 (`vacantia.andymallcco.dev`) — el dominio anterior fue dado de baja del todo en Infra Fase 5.

### Backend — Fase 8: Autenticación y roles (completa)

- [x] 8.1 Instalar `djangorestframework-simplejwt` + `django-cors-headers`; configurar autenticación híbrida (JWT de acceso en memoria del lado del cliente, refresh token en cookie `httpOnly`).
- [x] 8.2 Crear los 3 Groups de Django (`Administrador`, `Reclutador`, `Postulante`) vía migración de datos.
- [x] 8.3 Nueva app `apps/accounts`: modelo `ApplicantProfile` (uno a uno con el usuario — tipo y número de documento, nacionalidad, fecha de nacimiento, sexo, teléfono, departamento/provincia/distrito) + endpoints `login`/`refresh`/`logout`.
- [x] 8.4 Servicio de ubigeos (`departamento`/`provincia`/`distrito` seleccionables) consumiendo `free.e-api.net.pe/ubigeos.json` como fuente, cacheado del lado del backend (no se le pega en vivo por cada request) — el frontend consume un endpoint propio, no la API externa directo.

### Backend — Fase 9: Puestos y postulaciones (completa)

_9.1-9.3 desplegadas y verificadas en producción el 2026-08-10 (rutas, `pypdf` instalando bien en el contenedor, volumen de `media/` compartido con `celery-worker`, y llamada real a DeepSeek desde el worker en producción, todo confirmado con una postulación de prueba end-to-end)._

- [x] 9.1 Modelo `Puesto` (título, descripción, requisitos, creado por un reclutador) + endpoints CRUD (solo Reclutador puede crear/editar).
- [x] 9.2 Modelo `Postulacion` (postulante + puesto + CV + estado: pendiente/rechazado/aprobado) + endpoint público para postular (sube CV, sin necesitar cuenta).
- [x] 9.3 Extraer texto del CV (`pypdf` u similar) + tarea Celery que le pasa ese texto + la descripción del puesto al LLM (reutilizando `LLMProvider`/`DeepSeekLLM`, sin patrón nuevo) para evaluar el fit. _(Nota: cubre CVs digitales normales, con texto seleccionable. Si en las pruebas aparecen CVs escaneados como imagen, sin texto embebido, ahí se evalúa sumar OCR — no se construye de entrada para un caso que puede no aparecer.)_
- [x] 9.4 Si aprueba: crear el usuario + perfil automáticamente, asignarlo al Group Postulante, mandar credenciales por email (Resend vía `django-anymail`, ver `docs/Email/Resend/`). Si rechaza: no se crea nada, termina ahí. Si el email ya tenía cuenta de una aprobación anterior, no se duplica: se le resetea la contraseña y se manda un email nuevo (ver DECISIONS.md). _Desplegada y verificada en producción el 2026-08-11 — creación de cuenta y envío real por Resend confirmados con el key de `vacantia-prod`. Dominio propio `mail.andymallcco.dev` verificado en Resend el mismo día (DKIM+SPF por Porkbun) — ya entrega a cualquier destinatario real, no solo al email de la cuenta de Resend._
- [x] 9.5 Conectar `Interview` al usuario autenticado (`/api/ask/` usa `request.user` si viene un JWT válido, sigue funcionando anónimo si no — ver DECISIONS.md). El cierre real de acceso anónimo se hace en Frontend Fase 5.4, no acá.
- [x] 9.6 Contextualizar la entrevista con el puesto real (agregado 2026-08-11 — al planear la "sala de espera" de Frontend Fase 7, surgió que Gaby entrevista a todos igual, sin saber a qué puesto postuló el candidato ni sus requisitos; en Fase 9.5 se había dejado explícitamente afuera la conexión `Interview`↔`Postulacion` por no tener un uso concreto todavía — ahora sí lo hay).
  - [x] 9.6.1 Campo `Interview.postulacion` (`ForeignKey` nullable a `apps.recruiting.models.Postulacion`, `on_delete=SET_NULL`) — migración `interviews.0003_interview_postulacion` aplicada.
  - [x] 9.6.2 En `apps/interviews/views.py` (`ask`), al crear una `Interview` nueva para un usuario autenticado: busca la `Postulacion` aprobada más reciente por email (`apps/recruiting/services/postulacion_lookup.py`, service compartido — reusado también en 9.6.4, mismo criterio de matching que `account_provisioning.py`) y la conecta en `postulacion=`.
  - [x] 9.6.3 `ask_llm_task` arma un `system_prompt` contextual cuando la `Interview` tiene `postulacion` (`apps/interviews/services/interview_prompt_service.py`, título/descripción/requisitos del puesto), reusando el parámetro `system_prompt` opcional de `LLMProvider.ask()`. Sin `postulacion` conectada (demo anónima), sigue usando el `INTERVIEW_SYSTEM_PROMPT` genérico de siempre.
  - [x] 9.6.4 Endpoint `GET /api/postulaciones/mia/` (autenticado, `apps/recruiting/views.py::mi_postulacion`) — devuelve `nombre` + `puesto.titulo` de la `Postulacion` aprobada más reciente del usuario logueado; 404 si no hay ninguna. Registrado antes del router en `urls.py` para que no lo capture el patrón `<pk>` de `postulaciones/<pk>/`.

_9.6 completa y probada — 74 tests pasando en toda la suite del backend._

- [x] 9.8 Endpoint de detalle de entrevista para el panel de reclutador (agregado 2026-08-12, soporte de Frontend 6.3). Hoy no existe forma de consultar una `Interview` puntual por la API, solo crear/continuar vía `/api/ask/`.
  - [x] 9.8.1 `GET /api/interviews/<id>/` (`apps/interviews/views.py::interview_detail`) — devuelve `status`, `created_at`, los datos de la `Postulacion` conectada (`nombre`, `puesto_titulo`, `estado`, `resultado_filtro`) y la lista de preguntas con su respuesta (`question`, `created_at`, `answer`, `answered_at`), en orden cronológico.
  - [x] 9.8.2 Permiso nuevo `IsOwnerReclutadorOfInterview` (`apps/interviews/permissions.py`, mismo patrón que `CanManagePostulacion` de `apps/recruiting/permissions.py`): solo el Reclutador dueño del puesto de esa postulación puede ver la entrevista. Si la `Interview` no tiene `postulacion` (demo anónima, sin cuenta), no le pertenece a ningún reclutador — 403.
  - [x] 9.8.3 `PostulacionSerializer` (`apps/recruiting/serializers.py`) gana `interview_id` (nullable, `SerializerMethodField` sobre `obj.interviews.all()` vía el `related_name="interviews"` del FK agregado en 9.6.1 — `prefetch_related("interviews")` en `PostulacionViewSet.get_queryset` para evitar N+1) para que el frontend sepa si ya existe una entrevista que mostrar.
  - [x] 9.8.4 Tests: reclutador dueño ve el detalle completo con transcripción; otro reclutador (no dueño) recibe 403; anónimo recibe 401/403; entrevista sin postulación (demo) recibe 403; postulación sin entrevista trae `interview_id: null` en el listado, con entrevista trae su id. 55/55 tests pasando en `apps/interviews` + `apps/recruiting`.

### Gateway — Fase 5: Autenticación

- [x] 5.1 Recibir el JWT del cliente en el handshake de Socket.io y reenviarlo como header `Authorization` en cada llamada REST a Django (solo en `/api/ask/`, que es la que usa `request.user` desde Backend Fase 9.5).

### Frontend — Fase 5: Postulación y acceso de postulante

- [x] 5.1 Instalar `react-router`, estructura de `pages/` (ver `docs/ARCHITECTURE.md`). La pantalla de entrevista existente se movió a `pages/InterviewPage.tsx` sin cambiar su comportamiento — confirmado visualmente, mismo diseño y funcionamiento.
- [x] 5.2 Pantalla pública de postulación (`pages/ApplyPage.tsx`, ruta `/postular`) — sin login. Grilla de puestos abiertos (filtrados en el frontend por `estado === "abierto"`) con `PuestoCard`, click lleva al formulario (nombre/email/CV) contra `POST /api/postulaciones/`, con pantalla de confirmación al final. Probado end-to-end en el navegador.
- [x] 5.3 Pantalla de login para postulantes ya aprobados (`pages/LoginPage.tsx`, ruta `/login`) — `AuthContext` guarda el access token en memoria (nunca `localStorage`, ver DECISIONS.md Fase 8). Redirige a `/` al loguear; probado end-to-end con una cuenta real.
- [x] 5.4 Proteger la pantalla de entrevista (requiere estar logueado) — `RequireAuth` redirige a `/login` si no hay sesión. Probado end-to-end: login → chat funciona → `Interview` queda asociada al usuario en el admin.

_Frontend 5.1-5.4 + Gateway 5.1 desplegados y verificados en producción el 2026-08-11 — incluyó agregar `location /api/` en el Nginx del servidor (antes solo `/`, `/socket.io/`, `/media/`), fix de fallback de SPA en el nginx del contenedor `frontend` (ver DECISIONS.md), y `VITE_API_URL` en el `.env` de producción. Confirmado end-to-end en `interviewer.andymallcco.dev`: postular → login → chat → `Interview` asociada al usuario en el admin._

### Frontend — Fase 7: Arreglar el flujo del candidato (agregado 2026-08-11, tras revisar P.5/P.6 en producción)

**Contexto:** al revisar el flujo completo ya desplegado, aparecieron tres problemas de navegación/UX reales, no cosméticos:
1. La ruta raíz `/` es la entrevista (protegida) y `/postular` es secundaria — al revés de lo que tiene sentido: un candidato nuevo que entra al dominio debería caer en la página pública de vacantes, no en un login pidiendo credenciales que todavía no tiene.
2. Login lleva directo al chat en vivo con Gaby, sin ningún paso intermedio que le avise al candidato qué va a pasar.
3. **Bug funcional, no solo estético:** el logo "Vacantia" de la navbar linkea a `/postular` y está siempre clickeable, incluso en medio de una entrevista activa. Si el candidato navega afuera por error, `useSocket` desconecta el socket en el cleanup del efecto, y el `interview_id` que el gateway trackeaba (closure por conexión en `interviewSocket.ts`) se pierde — al volver a `/`, arranca una `Interview` nueva de cero, la anterior queda a medias, sin ninguna advertencia previa.

- [x] 7.1 Reordenar rutas: `/` pasa a ser `ApplyPage` (pública), la entrevista se movió a `/entrevista` (protegida con `RequireAuth`). Logo de `Navbar` ahora linkea a `/`, `LoginPage` redirige a `/entrevista` al loguear. Probado end-to-end: `/` anónimo muestra los puestos, login lleva a `/entrevista`.
- [x] 7.2 Pantalla de "sala de espera" antes del chat en vivo — `hasStarted` (estado local en `InterviewPage`) gatea el chat real. Tarjeta de bienvenida personalizada vía `fetchMiPostulacion` (`lib/api.ts`, llama a `GET /api/postulaciones/mia/`) — sin `Postulacion` aprobada (demo anónima o sin match), cae al saludo genérico sin romper. Botón "Empezar entrevista" revela `QuestionDisplay`/`TextAnswerForm`/`VoiceRecorder`. Probado end-to-end con una cuenta real: "¡Hola Andy Mallcco! Vas a tener una entrevista técnica para el puesto de Desarrollador Backend Python."
- [x] 7.3 Bloquear la salida accidental de una entrevista activa sin terminar. `useBlocker` de `react-router` (soportado por `createBrowserRouter`) dentro de `InterviewPage`, activo mientras `hasStarted && !isFinished` — bloquea cualquier navegación in-app (logo, back del navegador) con `window.confirm` antes de dejar salir; además `window.onbeforeunload` para cerrar pestaña/refrescar. Probado end-to-end: click en el logo en medio de una entrevista muestra el confirm, "Cancelar" te deja adentro, "Aceptar" te saca.

### Backend 9.7 + Gateway 5.2 + Frontend 7.4: una entrevista por puesto, no una por cuenta (agregado 2026-08-11)

**Contexto:** al usar 7.1-7.3, surgió la duda de qué pasa si la misma persona postula (y es aprobada) para más de un puesto con el mismo email — la cuenta se reusa (ver DECISIONS.md, provisioning unificado), pero hoy `/api/postulaciones/mia/` y el armado de `Interview.postulacion` (Backend 9.6.2) asumen ciegamente "la postulación aprobada más reciente", sin dejarle elegir a la persona ni evitar que se repita una entrevista para el mismo puesto.

**Decisión de producto:** una entrevista **por postulación aprobada**, no una sola por cuenta — coherente con que Gaby ya pregunta cosas específicas de cada puesto (Fase 9.6) y con cómo funcionan los ATS reales (cada postulación tiene su propio proceso, aunque sea la misma persona aplicando a varios roles). Implica: si tiene más de un puesto aprobado sin entrevistar, se le deja elegir cuál; una vez hecha la entrevista de un puesto, no se puede repetir para esa misma postulación.

- [x] 9.7.1 Backend: `apps/recruiting/services/postulacion_lookup.py` — nueva función `get_postulaciones_aprobadas_pendientes(email)` que devuelve las `Postulacion` con `estado=aprobado` **sin** una `Interview` asociada todavía (`interviews__isnull=True`, usando el `related_name="interviews"` del FK agregado en 9.6.1). La función vieja (`get_ultima_postulacion_aprobada`) se mantiene tal cual para donde no aplica esta lógica (`account_provisioning.py` sigue queriendo "la más reciente" para saber a quién mandarle el email, eso no cambia).
- [x] 9.7.2 Backend: `GET /api/postulaciones/mia/` (`apps/recruiting/views.py::mi_postulacion`) pasa a devolver una **lista** de postulaciones pendientes de entrevistar (vacía, una, o varias — siempre 200, ya no 404), con `id` incluido en cada una para poder mandarlo de vuelta en 9.7.3.
- [x] 9.7.3 Backend: `POST /api/ask/` (`apps/interviews/views.py::ask`) deja de adivinar la postulación — al crear una `Interview` nueva, recibe un `postulacion_id` explícito y opcional en el body. Valida que esa `Postulacion` sea `aprobada` y del email del usuario autenticado (404 si no), que no tenga ya una `Interview` (409 si la tiene), y que haya un usuario autenticado si se manda `postulacion_id` (401 si no). Sin `postulacion_id`, la `Interview` se crea sin `postulacion` (demo/sin match), como antes.
- [x] 9.7.4 Gateway: **decisión de diseño distinta a la planeada originalmente** — en vez de mandar `postulacionId` en el handshake del socket (como el JWT), se manda como segundo argumento de los eventos `ask`/`audio` (`socket.emit("ask", question, postulacionId)`). Motivo: el socket se conecta al montar `InterviewPage`, antes de que la persona elija en el selector (9.7.5) — el handshake ya pasó para cuando se sabe el `postulacionId`, así que tenía que viajar en el evento, no en la conexión. `djangoClient.ts::askQuestion` y `interviewSocket.ts` actualizados.
- [x] 9.7.5 Frontend: `InterviewPage.tsx` usa `fetchMisPostulacionesPendientes` — con más de una pendiente, muestra un selector (lista de puestos, clickeable) antes de la sala de espera; con una sola, se elige sola sin mostrar el selector (7.2 sin cambios visibles); con cero, saludo genérico de siempre (demo/sin match). El `postulacion_id` elegido viaja en cada `askQuestion`/`sendAudio`, aunque el backend solo lo usa en el primer mensaje (una vez creada la `Interview`, ya no hace falta).
- [x] 9.7.6 Frontend: aviso al terminar una entrevista si quedan más postulaciones pendientes (agregado 2026-08-12, encontrado al probar 9.7.5 en el navegador). Sin esto, alguien con varias postulaciones aprobadas no tiene forma visual de enterarse que le queda otra entrevista por hacer — tendría que adivinar que hay que recargar `/entrevista` a mano.
  - Al terminar (`isFinished`), `InterviewPage` vuelve a pedir `fetchMisPostulacionesPendientes`. Si devuelve alguna, muestra un aviso con un link "Continuar con mi próxima entrevista".
  - Ese link es un `<a href="/entrevista">` normal, **no** un `<Link>` de React Router — hace falta una recarga real del navegador, no solo un cambio de ruta. Motivo técnico: el `interview_id` de la entrevista activa vive en una variable en memoria dentro de la conexión de socket actual (`let interviewId` en `interviewSocket.ts`, cerrada sobre esa conexión puntual) — una vez seteada, el gateway la reusa para todo mensaje de esa misma conexión, ignorando cualquier `postulacion_id` nuevo (Backend 9.7.3). Para arrancar una entrevista distinta hace falta una conexión de socket nueva, y React Router no garantiza eso si el destino es la misma ruta en la que ya se está — solo una recarga completa de página fuerza que `useSocket` se vuelva a montar de cero.
  - Probado end-to-end en local con una cuenta de tres postulaciones aprobadas: selector → entrevista 1 → "Tiene entrevistas pendientes" → recarga real → sala de espera de la siguiente postulación, sin selector (quedaba solo una).

_9.7 completo, probado end-to-end en local: selector con dos postulaciones aprobadas, elección respetada (verificado en la base de datos que la `Interview` quedó ligada al puesto elegido, no al otro), y auto-selección sin selector al quedar una sola pendiente. 93/93 tests del backend pasando._

### Frontend — Fase 6: Panel de reclutador (completa)

**Diseño:** acá sí va sidebar (componente `Sidebar` de shadcn/ui) — a diferencia de las pantallas del candidato (ver P.5), el dashboard tiene varias vistas reales (puestos, postulaciones, detalle de entrevista) que se benefician de navegación lateral. Tablas con el componente `Table` de shadcn, `Badge` para los estados (pendiente/aprobado/rechazado, con color por estado), y algún gráfico simple (postulaciones por estado) con el componente `Chart` de shadcn si aporta valor real — no decorativo. **Nota (6.2):** se evaluó `@tanstack/react-table` para sorting/paginación pero la versión instalada (9.1.2) resultó ser una reescritura mayor con una API completamente distinta a la v8 estable documentada (no exporta `useReactTable`/`getCoreRowModel`/`flexRender`) — se descartó la dependencia y las tablas se renderizan con `.map()` plano sobre los primitivos `Table` de shadcn, ya que hoy no se usa sorting/paginación real. Si se necesita más adelante, reinstalar fijando `@tanstack/react-table@^8` explícitamente.

- [x] 6.1 Login de reclutador — reusa `LoginPage`/`AuthContext` que ya existen (mismo endpoint `/api/auth/login/`, no se duplica el mecanismo). El rol viaja como claim custom en el JWT (`CustomTokenObtainPairSerializer`, ver DECISIONS.md 2026-08-12) — `AuthContext` lo decodifica al loguear, `LoginPage` redirige a `/dashboard` (Reclutador) o `/entrevista` (Postulante); `/dashboard` protegida con `RequireRole` (extiende `RequireAuth`). Probado end-to-end con una cuenta de reclutador real: login → `/dashboard`; un Postulante no puede entrar a `/dashboard` a mano, y viceversa.
- [x] 6.2 Dashboard con sidebar (`DashboardLayout.tsx`, componente `Sidebar` de shadcn, nav "Puestos"/"Postulaciones"). Backend: `PuestoViewSet` soporta `?mias=true` (filtra por `creado_por`, `Puesto.objects.none()` si no autenticado) y anota `postulaciones_count` (`Count("postulaciones")`); `PostulacionViewSet` agrega `select_related("puesto")` y expone `puesto_titulo` (campo `source="puesto.titulo"`) para evitar joins del lado del cliente. Frontend: `PuestosPage.tsx` (tabla título/estado/cantidad de postulaciones) y `PostulacionesPage.tsx` (tabla nombre/email/puesto/estado con `Badge` por color). Tests: `test_mias_filter_returns_only_the_reclutador_own_puestos`, `test_mias_filter_returns_empty_for_anonymous`, `test_puesto_list_includes_postulaciones_count` en `apps/recruiting`. Probado en navegador con una cuenta de reclutador real.
- [x] 6.3 Vista de detalle de una entrevista completada (transcripción + resultado del filtro de CV), agregado 2026-08-12. Usa Backend 9.8 (`GET /api/interviews/<id>/` + `interview_id` en `PostulacionSerializer`).
  - [x] 6.3.1 Botón "Ver entrevista" en cada fila de `PostulacionesPage.tsx` — visible solo si `interview_id` no es `null`. Usa `Button` de shadcn con `render={<Link .../>}` + `nativeButton={false}` (Base UI exige avisar explícitamente cuando el botón renderiza como otro elemento, ej. un `<a>`, en vez de un `<button>` nativo).
  - [x] 6.3.2 Página nueva `pages/dashboard/InterviewDetailPage.tsx`, ruta `/dashboard/entrevistas/:id` (child de `DashboardLayout`, mismo `RequireRole` que el resto del panel) — muestra el resultado del filtro de CV (`resultado_filtro` + `Badge` de estado) y la transcripción completa (pregunta/respuesta en orden, versión de solo lectura, distinta del `QuestionDisplay` del candidato que depende del socket en vivo).
  - [x] 6.3.3 `fetchInterviewDetail(token, interviewId)` en `lib/api.ts`.

_9.8 + 6.3 probados end-to-end en local: reclutador dueño ve la transcripción completa de una postulación de prueba con entrevista finalizada._

### Backend 9.9 + Frontend 7.5: página de detalle de puesto, formato real de oferta, y categorías (agregado 2026-08-13, completa)

**Contexto:** hoy `ApplyPage` muestra el título/descripción/requisitos completos de cada puesto directo en la card de la grilla — no hay una página de detalle propia, y `Puesto` no tiene categoría/área. Al revisar cómo se ven las ofertas reales (LinkedIn, Computrabajo), surgieron tres mejoras encadenadas.

**Decisión 1 — página de detalle, no modal:** cada puesto pasa a tener su propia URL (`/puestos/:id`), coherente con el patrón que ya usa el resto del proyecto (una pantalla = una ruta, no modales). La card en `ApplyPage` se vuelve un preview compacto (título, área, 1-2 líneas de resumen) que linkea al detalle — el layout de esa página de detalle debe organizarse en secciones claras (no un bloque de texto centrado), acercándose al formato de LinkedIn/Computrabajo.

**Decisión 2 — formato de oferta más real:** `Puesto` gana campos nuevos, separando lo que hoy vive todo mezclado en `descripcion`:
- `descripcion` se mantiene como resumen general del rol.
- `funciones` (nuevo, `TextField`) — responsabilidades del día a día.
- `requisitos` se mantiene (obligatorios).
- `requisitos_deseables` (nuevo, `TextField`, opcional) — nice-to-have, separado de los obligatorios.
- `modalidad` (nuevo, choices: `presencial`/`remoto`/`hibrido`).

**Decisión 3 — categorías como tabla propia, no `choices`:** se investigaron categorías reales (Computrabajo Perú: Ventas, Atención a Clientes, Recursos Humanos, Almacén/Logística/Transporte, Administración/Oficina, Contabilidad/Finanzas, Producción/Operarios/Manufactura, Mantenimiento y Reparaciones Técnicas, Servicios Generales/Aseo/Seguridad, Medicina/Salud, CallCenter/Telemercadeo; LinkedIn usa una taxonomía de 26 "funciones" más corporativa: IT, Data/Research, Marketing, Legal, Consulting, etc.). Se decidió modelar `Categoria` como su propio modelo (`nombre`), **no** un `TextChoices` en `Puesto` — mismo patrón que ya se usó para los Groups (`accounts/migrations/0002_create_groups.py`): una migración de datos siembra un set curado inicial (mezcla de ambas fuentes + los rubros que mencionó el usuario: Tecnología/Sistemas, Análisis de Datos, Recursos Humanos, Ventas, Atención al Cliente, Administración, Contabilidad/Finanzas, Marketing, Logística/Almacén, Producción/Operaciones, Mantenimiento Técnico, Servicios Generales/Limpieza/Seguridad, Legal, Consultoría, Salud, Educación, Call Center), editable después desde el admin de Django **sin deploy de código** — a diferencia de `choices`, que requiere migración + deploy para agregar una categoría nueva. `Puesto.categoria` pasa a ser FK (`on_delete=PROTECT`, para no perder la categoría de puestos existentes si se borra una por error).

- [x] 9.9.1 Backend: modelo `Categoria` (`apps/recruiting/models.py`) + migración de datos (`0004_seed_categorias.py`) que siembra el set curado inicial (mismo patrón que `0002_create_groups.py`), registrada en el admin. **Nota operativa:** la primera migración (`0003_categoria_puesto_categoria`) se generó por error con `docker exec` (el contenedor no tiene el código montado en vivo, así que el archivo nunca llegó al repo) — hubo que regenerarla con el venv nativo. De acá en más, cualquier comando que **escriba archivos** (`makemigrations`, etc.) se corre nativo; `docker exec` solo para aplicar migraciones ya existentes o correr la app.
- [x] 9.9.2 Backend: `Puesto` gana `categoria` (FK, nullable), `funciones`, `requisitos_deseables` (ambos `TextField` opcionales), `modalidad` (`TextChoices`: presencial/remoto/híbrido, default presencial) — migración de esquema aplicada.
- [x] 9.9.3 Backend: `PuestoSerializer` expone los campos nuevos + `categoria_nombre` (`SerializerMethodField`-like vía `source="categoria.nombre"` con `default=None` para cuando no hay categoría); `PuestoViewSet` soporta `?categoria=<id>`. Nuevo `CategoriaViewSet` (`ReadOnlyModelViewSet`, público) en `/api/categorias/` para que el frontend pueble el filtro.
- [x] 9.9.4 Frontend: `PuestoCard.tsx` reescrito como preview compacto (título, badge de categoría, resumen de 2 líneas, badge de modalidad) que linkea a `/puestos/:id` — ya no abre el formulario directo. `ApplyPage.tsx` gana el filtro por categoría (`Select` de shadcn/Base UI). **Nota técnica:** a diferencia de Radix, el `Select` de Base UI no muestra automáticamente el label del item seleccionado — hay que pasarle una función de formato como children de `SelectValue` (`{(value) => ...}`), si no muestra el `value` crudo. También el popup hereda el ancho del trigger (`w-(--anchor-width)`), así que el trigger necesita un ancho fijo (`className="w-72"`) para no cortar nombres de categoría largos.
- [x] 9.9.5 Frontend: página nueva `pages/PuestoDetailPage.tsx`, ruta `/puestos/:id` (pública) — secciones claras (descripción, funciones, requisitos, requisitos deseables) separadas con `Separator`, badges de categoría/modalidad. El botón "Postular a este puesto" revela el formulario (nombre/email/CV) más abajo en la misma página, en vez de navegar a otra ruta — mismo patrón de confirmación que tenía `ApplyPage` antes. `PuestoCardSkeleton.tsx` ajustado a la forma nueva de la card.
- [x] 9.9.6 Tests backend: `test_categorias.py` (la migración siembra el set esperado), tests en `test_views.py` (`categoria_nombre` presente/null, filtro `?categoria=<id>`, endpoint `/api/categorias/` público). 37/37 tests de `apps/recruiting` pasando.

_Probado end-to-end en local: filtro por categoría, página de detalle con las secciones completas, y el flujo de postulación completo (formulario → confirmación) desde la página de detalle._

**Confirmado explícitamente, no cambia:** el proyecto sigue siendo para **una sola empresa** (varios reclutadores propios, no un marketplace multi-empresa tipo LinkedIn Jobs) — eso sería un cambio de arquitectura mayor (modelo `Empresa`, aislamiento entre tenants), no una feature más, y no está planeado.

### Backend 9.10 + Frontend 6.4: avance a la siguiente etapa y vacantes por puesto (agregado 2026-08-13, completa — revisado el mismo día tras aclarar el alcance real del producto)

**Contexto:** al revisar el panel de reclutador (6.3), surgió que hoy no hay ninguna forma de registrar qué pasa con un candidato después de la entrevista con Gaby — `Postulacion.estado` es el resultado del filtro de CV (gate para crear la cuenta), y `Interview.status` es solo si la entrevista se hizo o no. Ninguno de los dos captura una decisión del reclutador sobre el candidato.

**Qué es Vacantia realmente, y qué no es (esto cambió el diseño de esta fase):** el primer diseño de esta fase usaba una decisión `contratado`/`no_contratado`, pero eso no refleja cómo funciona un proceso de selección real. Vacantia automatiza/asiste **dos etapas tempranas y de alto volumen**: el filtro de CV (Fase 9.3, IA lee el CV y evalúa el fit contra el puesto) y una primera entrevista conversacional (Gaby, contextualizada al puesto). Lo que **no** hace, y no debería hacer, es una entrevista técnica real con código en vivo (pair programming, sistema de diseño) — eso lo sigue dando una persona, fuera de este sistema. Por eso la decisión del reclutador después de la entrevista con Gaby no es "contratar", es **"¿este candidato avanza a la siguiente etapa (entrevista técnica real) o no?"** — la contratación final queda fuera del alcance de Vacantia.

**Decisión 1 — la decisión es manual, no de IA:** a diferencia del filtro de CV (pre-filtro de volumen, reversible y de bajo riesgo), decidir si alguien avanza es un juicio humano — no se automatiza. Campo nuevo `Interview.decision` (`TextChoices`: `pendiente`/`avanza`/`no_avanza`, default `pendiente`), seteado a mano por el reclutador desde `InterviewDetailPage` después de leer la transcripción y el resultado del filtro de CV. Va en `Interview`, no en `Postulacion` — así no se pisa/pierde el resultado del filtro de CV (`Postulacion.estado`), que es un dato distinto e independiente. Igual que el resultado del filtro de CV, el candidato **nunca** ve esta decisión desde su lado (mismo criterio ya establecido en DECISIONS.md).

**Decisión 2 — `Puesto.vacantes` (entero, default 1):** cuántas personas busca finalmente ese puesto. El panel de reclutador muestra, por separado (no como una fracción "X/N" — Vacantia no sabe si un preseleccionado termina contratado, esa decisión pasa después, fuera del sistema): la cantidad de `vacantes` buscadas, y la cantidad de candidatos que `avanzan` (preseleccionados) para ese puesto.

**Decisión 3 — el cierre del puesto sigue siendo manual:** el puesto **no** se cierra solo por ningún motivo automático — el reclutador lo cierra a mano (ya existe `Puesto.estado`, no se toca ese mecanismo). Motivo: la contratación final ocurre fuera de Vacantia, así que el sistema no tiene forma de saber cuándo el puesto está realmente cubierto.

**Escalabilidad — cómo se calcula el contador sin N+1:** igual que `postulaciones_count` en `PuestoSerializer` (Fase 6.2), el conteo de preseleccionados se anota en el queryset de `PuestoViewSet` con `Count`, no se calcula en Python iterando — una sola query trae todos los puestos con su contador ya resuelto, sin importar cuántos puestos/postulaciones/entrevistas haya:
```python
Puesto.objects.annotate(
    preseleccionados=Count(
        "postulaciones__interviews",
        filter=Q(postulaciones__interviews__decision=Interview.Decision.AVANZA),
    )
)
```

- [x] 9.10.1 Backend: `Interview.decision` (`TextChoices`: `pendiente`/`avanza`/`no_avanza`, default `pendiente`) — migración de esquema aplicada.
- [x] 9.10.2 Backend: `Puesto.vacantes` (`PositiveIntegerField`, default 1) — migración de esquema aplicada.
- [x] 9.10.3 Backend: `PATCH /api/interviews/<id>/decision/` (`update_interview_decision`), protegido con `IsOwnerReclutadorOfInterview` (9.8.2). Valida que el valor esté en `Interview.Decision.values` (400 si no). `interview_detail` también expone `decision` ahora.
- [x] 9.10.4 Backend: `PuestoSerializer` anota `preseleccionados` (`Count` con `filter=Q(postulaciones__interviews__decision=AVANZA)`, mismo patrón que `postulaciones_count`) y expone `vacantes`.
- [x] 9.10.5 Frontend: `InterviewDetailPage.tsx` — card "Decisión" con badge de estado + botones "Avanza a la siguiente etapa"/"No avanza", confirmados con `window.confirm` (mismo patrón que el bloqueo de salida de `InterviewPage`, no se instaló `AlertDialog` para esto). Cada botón se deshabilita solo cuando **su propia** decisión ya es la actual — el otro se deja habilitado a propósito, para poder revertir la decisión si el reclutador se equivocó o reconsidera.
- [x] 9.10.6 Frontend: `PuestosPage.tsx` — columnas "Vacantes" y "Preseleccionados" agregadas a la tabla.
- [x] 9.10.7 Tests backend: `Interview.decision` se puede leer/actualizar (dueño), 403 para otro reclutador, 400 con valor inválido, 401/403 sin autenticar; `preseleccionados` cuenta solo `avanza` (no `no_avanza` ni `pendiente`) en `apps/recruiting`. 75/75 tests de `apps/interviews` + `apps/recruiting` pasando.

_Probado end-to-end en local: decisión pendiente por default, cambio a "avanza" confirmado con `window.confirm`, badge y botones reflejan el estado nuevo correctamente, el botón contrario queda habilitado para poder revertir._

### Backend 9.11 + Frontend 6.5: gestión completa de puestos desde el dashboard (crear, editar, cerrar) (agregado 2026-08-19)

**Contexto:** al auditar la documentación se encontró que no hay ninguna forma de dar de alta, editar o cerrar un `Puesto` desde el dashboard del reclutador — hoy solo se puede a mano desde el admin de Django. No es una decisión de producto, es simplemente algo que nunca se construyó: `PuestoViewSet` (9.1) ya es un `ModelViewSet` completo con `IsOwnerReclutadorOrReadOnly` (permiso escrito explícitamente para esto: "solo un Reclutador puede crear, y solo el que lo creó puede editar/borrar ese puesto"), y `PuestoSerializer` ya tiene todos los campos de negocio como escribibles — el backend no necesita CRUD nuevo, solo cerrar un hueco real encontrado en el camino (ver Decisión 2) y construir la UI que falta.

**Decisión 1 — un solo formulario para crear y editar, no dos componentes:** `PuestoFormPage.tsx` recibe un `id` opcional de la URL (`/dashboard/puestos/nuevo` vs `/dashboard/puestos/:id/editar`) — con `id`, hace `GET` para precargar los campos y `PATCH` al guardar; sin `id`, `POST`. Mismo patrón de `useState` por campo que el resto de los formularios del proyecto (`LoginPage`, el formulario de postulación en `PuestoDetailPage`) — no se introduce `react-hook-form`/`zod` ni ninguna dependencia nueva solo para este formulario, sería inconsistente con el resto de la base y no aporta nada que el patrón actual no resuelva ya.

**Decisión 2 — hallazgo real: `Puesto.estado` (abierto/cerrado) no bloquea nada hoy.** Al diseñar el botón "cerrar puesto" se encontró que el campo es puramente decorativo: `ApplyPage` lista **todos** los puestos sin filtrar por `estado`, y crear una `Postulacion` no valida el `estado` del `Puesto` — un puesto "cerrado" hoy sigue apareciendo en la postulación pública y sigue aceptando CVs nuevos. Esto se cierra en el mismo paso (9.11.2/9.11.3 abajo), porque un botón de "cerrar puesto" que no cierra nada sería peor que no tenerlo — daría una falsa sensación de control.

**Decisión 3 — cerrar/reabrir es una acción de un solo campo en la tabla, no parte del formulario:** botón por fila en `PuestosPage.tsx` (`PATCH {estado: "cerrado"}`), no obliga a abrir el formulario completo de edición para cambiar un solo campo. Confirmado con `AlertDialog` (mismo patrón ya establecido en P.8.1) antes de cerrar, ya que ahora sí tiene una consecuencia real: deja de aceptar postulaciones nuevas.

**Decisión 4 — `vacantes` mínimo 1, validado en el backend, no solo en el frontend:** hoy `Puesto.vacantes` es un `PositiveIntegerField` (acepta 0), pero un puesto con 0 vacantes no tiene sentido de negocio. Se agrega `MinValueValidator(1)` al campo del modelo (migración de esquema, sin tocar datos existentes — no debería haber ningún `Puesto` en 0) para que la regla viva en el modelo (se aplica sin importar qué cliente llame a la API), no solo como validación de UI.

- [x] 9.11.1 Backend: `Puesto.vacantes` gana `validators=[MinValueValidator(1)]` — migración de esquema (`0007_alter_puesto_vacantes`) aplicada.
- [x] 9.11.2 Backend: `PuestoViewSet.get_queryset()` — el listado público (`self.action == "list"`, sin `?mias=true`) filtra `estado=Puesto.Estado.ABIERTO`; con `?mias=true` se siguen mostrando todos. El `retrieve` (detalle) no se filtra a propósito — lo necesita 9.11.6 para poder cargar un puesto cerrado y mostrar el aviso, en vez de un 404.
- [x] 9.11.3 Backend: `PostulacionSerializer.validate_puesto` — rechaza con 400 ("Este puesto ya no acepta postulaciones.") si `puesto.estado != Puesto.Estado.ABIERTO`. Validación a nivel de serializer (no en la vista), estilo DRF idiomático.
- [x] 9.11.4 Frontend: `PuestoFormPage.tsx` (crear/editar, ver Decisión 1) — campos `titulo`, `descripcion`, `funciones`, `requisitos`, `requisitos_deseables`, `modalidad` (`Select`), `vacantes` (number, min 1), `categoria` (`Select`, reusa `fetchCategorias` ya existente de 9.9). Rutas nuevas en `router.tsx`: `/dashboard/puestos/nuevo`, `/dashboard/puestos/:id/editar`, protegidas igual que el resto de `/dashboard` (`RequireRole` Reclutador).
- [x] 9.11.5 Frontend: `PuestosPage.tsx` — botón "Nuevo puesto" (linkea a 9.11.4), botón "Editar" y botón "Cerrar puesto"/"Reabrir puesto" por fila (con `AlertDialog` solo para cerrar, ver Decisión 3 — reabrir no tiene la misma consecuencia, no hace falta confirmar).
- [x] 9.11.6 Frontend: `PuestoDetailPage.tsx` — si `puesto.estado === "cerrado"`, oculta el formulario de postulación y muestra un aviso ("Este puesto ya no está aceptando postulaciones") en vez de dejar que el candidato lo intente y reciba el 400 de 9.11.3.
- [x] 9.11.7 Tests backend: crear/editar/cerrar solo por el reclutador dueño (403 para otro reclutador, 401 sin autenticar — ya cubierto desde 9.1), listado público excluye `cerrado` y `?mias=true` no, detalle sí devuelve un puesto `cerrado`, `Postulacion` a un puesto `cerrado` devuelve 400, `vacantes=0` rechazado. 44/44 tests de `apps/recruiting` pasando.
- [x] 9.11.8 Verificación end-to-end en el navegador: creado "Puesto de prueba CRUD 1" desde el dashboard, apareció en `/` (público), editado el título, cerrado (badge cambia a "cerrado", botón a "Reabrir puesto"), confirmado que desaparece de `/` y que `PuestoDetailPage` muestra "Este puesto ya no está aceptando postulaciones" en vez del formulario, reabierto y confirmado que vuelve a aparecer en `/`.

_Backend 9.11 + Frontend 6.5 completos — el reclutador ya puede crear, editar, cerrar y reabrir sus propios puestos desde el dashboard, sin pasar por el admin de Django; el bug de `estado` no aplicado se cerró en el mismo paso._

### Backend 8.5 + Frontend 7.6: completar el perfil del postulante (agregado 2026-08-19)

**Contexto:** `ApplicantProfile` (Backend 8.3) se crea automáticamente pero **vacío** al aprobar una postulación (Backend 9.4) — ningún campo (DNI, teléfono, ubigeo) se completa nunca, porque el frontend nunca construyó una pantalla para eso. El servicio de ubigeos (8.4) tampoco lo consume nadie: los 3 endpoints (`/api/auth/ubigeo/departamentos|provincias|distritos/`) existen desde Backend Fase 8 y no los llama ni una sola vista del frontend. Es el mismo tipo de hueco que 9.11: pieza de backend lista, sin la UI correspondiente.

**Decisión 1 — autoservicio opcional, no un paso obligatorio antes de la entrevista:** el plan original (ver `docs/DECISIONS.md`, pivote 2026-08-06) documentó explícitamente que estos datos son para elegibilidad legal/estadísticas, **nunca** criterio de filtro — no hay ninguna razón de negocio para bloquear el acceso a `/entrevista` hasta completarlos. Se agrega como una pantalla `/perfil` accesible desde el dropdown de cuenta de la `Navbar` (junto a "Cerrar sesión"), no como un gate obligatorio — mantiene la fricción mínima entre "cuenta aprobada" y "entrevista" que el resto del producto ya decidió proteger.

**Decisión 2 — `RetrieveUpdateAPIView` genérico, no una vista a mano:** a diferencia de las vistas de auth (`login`/`refresh`/`logout`, que necesitan lógica de cookie custom y no encajan en un genérico), leer/actualizar el perfil del usuario autenticado es exactamente el caso de uso de `generics.RetrieveUpdateAPIView` de DRF — `get_object()` devuelve `self.request.user.applicant_profile` en vez de buscar por `pk` en la URL (el endpoint no recibe id, siempre es "mi propio perfil"). Menos código a mano que un `@api_view` con `if request.method == "GET"/"PATCH"`.

- [x] 8.5.1 Backend: `ApplicantProfileSerializer` (`ModelSerializer`, todos los campos de `ApplicantProfile` menos `user`, editables).
- [x] 8.5.2 Backend: `PerfilView(generics.RetrieveUpdateAPIView)`, `permission_classes=[IsPostulante]`, `get_object` hace `get_or_create` sobre el perfil del usuario autenticado. Ruta `GET/PATCH /api/auth/perfil/`.
- [x] 8.5.3 Frontend: `PerfilPage.tsx`, ruta `/perfil` (protegida, `RequireRole` Postulante). Formulario con los campos de `ApplicantProfile` — `departamento`/`provincia`/`distrito` como 3 `Select` en cascada (cada uno se habilita/repuebla cuando el anterior cambia, consumiendo los 3 endpoints de ubigeo ya existentes desde 8.4). Al elegir un distrito se guarda también su `ubigeo_codigo` (viene en la misma respuesta de `/ubigeo/distritos/`).
- [x] 8.5.4 Frontend: entrada "Mi perfil" en el `DropdownMenu` de cuenta de `Navbar.tsx`, visible solo para el rol Postulante.
- [x] 8.5.5 Tests backend: `GET`/`PATCH` del propio perfil funciona (con creación automática del perfil en el primer acceso); un Reclutador no tiene acceso (403, `IsPostulante`); anónimo 401; actualizar con un `numero_documento` duplicado (mismo `tipo_documento`) devuelve 400, no 500 — confirmado que DRF ya genera el validador automáticamente para el `UniqueConstraint` condicional, sin necesitar código extra en el serializer. 28/28 tests de `apps/accounts` pasando.
- [x] 8.5.6 Verificado end-to-end en el navegador: "Mi perfil" desde el dropdown de cuenta, completado DNI/teléfono/nacionalidad/fecha de nacimiento/sexo/departamento→provincia→distrito en cascada (LIMA → LIMA → SAN MARTIN DE PORRES), guardado ("Perfil guardado."), y confirmado tras F5 que todo persiste.

_Backend 8.5 + Frontend 7.6 completos — el postulante ya puede completar su perfil (DNI, teléfono, ubigeo) desde "Mi perfil", autoservicio y sin bloquear el acceso a la entrevista._

### Frontend 6.6: selector de emojis en el formulario de puesto (agregado 2026-08-19)

**Contexto:** surgió al hablar de si el texto de un puesto admite emojis — ya los admite sin ningún cambio (son solo caracteres Unicode, Postgres y los inputs de React los guardan y muestran igual que cualquier otro texto), pero **escribirlos es fácil en celular** (el teclado del sistema siempre tiene el ícono de emoji a la vista) **e inconsistente en desktop** (`Win + .`, `Cmd + Ctrl + Space`, o nada en muchas distros de Linux — ningún atajo universal ni descubrible). Se agrega un selector propio en el formulario para no depender de que el reclutador sepa el atajo de su sistema operativo. Depende de que exista `PuestoFormPage.tsx` (Frontend 6.5) — no tiene sentido construirlo antes que el formulario donde va a vivir.

**Decisión 1 — componente propio y reusable dentro del formulario, no 5 instancias sueltas:** `EmojiPickerButton.tsx` (botón + popover con la grilla), usado una vez por cada campo de texto libre de `PuestoFormPage` (`titulo`, `descripcion`, `funciones`, `requisitos`, `requisitos_deseables`) — se construye una sola vez y se reusa, no se duplica la lógica del popover 5 veces.

**Decisión 2 — inserta en la posición del cursor, no al final del texto:** usando `selectionStart`/`selectionEnd` del `<textarea>`/`<input>` enfocado (vía `ref`), para que insertar un emoji a la mitad de una oración no rompa lo ya escrito — sin esto, el componente sería más una molestia que una ayuda.

**Decisión 3 — el popover usa `Popover` de shadcn (Base UI), no el popover propio de la librería de emojis:** mantiene la apariencia consistente con el resto de la app (tema claro/oscuro ya resuelto por las variables CSS existentes) — la librería externa solo aporta la grilla/búsqueda de emojis puertas adentro del `Popover` ya existente, no su propio contenedor visual.

- [x] 6.6.1 Instalada `emoji-picker-react@4.19.1` (`pnpm add`) — confirmado antes de instalar que su `peerDependencies` (`react: >=16`, sin tope superior) es compatible con React 19, vía `npm view`.
- [x] 6.6.2 `EmojiPickerButton.tsx` — botón con ícono `Smile` (`lucide-react`) que abre un `Popover` de shadcn (instalado con `npx shadcn@latest add popover`, no existía en el proyecto) con el componente `EmojiPicker`. El tema (claro/oscuro) se lee del `useTheme()` ya existente y se pasa explícito a `EmojiPicker` (`Theme.LIGHT`/`Theme.DARK`), en vez de dejarlo en modo `AUTO` — el toggle manual de tema de la app no siempre coincide con `prefers-color-scheme`, que es lo único que usaría `AUTO`.
- [x] 6.6.3 `hooks/useEmojiInsert.ts` — hook que recibe `(value, setValue)` de un campo y devuelve `{ ref, insertEmoji }`; `insertEmoji` lee `selectionStart`/`selectionEnd` del elemento para insertar en la posición del cursor (no al final), y reubica el cursor después del emoji insertado. **Hallazgo real al integrarlo:** la primera versión bundleaba `value`/`setValue`/`ref`/`insertEmoji` en un solo hook (`useEmojiField`), pero el lint (`react-hooks/refs`, del plugin nuevo de React Compiler) marcaba error en **cualquier** propiedad leída de ese objeto durante el render, no solo el `ref` — falso positivo conocido de esa regla cuando un hook devuelve un `ref` junto con otros campos en el mismo objeto. Se resolvió separando: `useState` plano por campo (mismo patrón que el resto de los formularios del proyecto) + `useEmojiInsert(value, setValue)` aparte, solo para el `ref`/`insertEmoji`, desestructurado en variables planas en el punto de uso (no `objeto.ref` dentro del JSX) — el lint quedó limpio y el código terminó más consistente con el resto de la base, no menos.
- [x] 6.6.4 `EmojiPickerButton` cableado junto a `titulo`, `descripcion`, `funciones`, `requisitos`, `requisitos_deseables` en `PuestoFormPage.tsx`, cada uno con su propio `useEmojiInsert`.
- [x] 6.6.5 Verificado en el navegador: emoji insertado a la mitad de un texto ya escrito en los 5 campos (título, descripción, funciones, requisitos, requisitos deseables), sin pisar lo existente. Guardado y confirmado que se ve igual en `PuestosPage` (tabla del dashboard), en el `PuestoDetailSheet` (6.7), y del lado público en `PuestoDetailPage`/`ApplyPage`.

_Frontend 6.6 completo — el reclutador puede insertar emojis en cualquier campo de texto del formulario de puesto, con un selector propio en vez de depender del atajo del sistema operativo._

### Frontend 6.7: vista de detalle de solo lectura en el dashboard (agregado 2026-08-19)

**Contexto:** al probar 9.11 end-to-end en el navegador, surgió que no hay forma de ver el detalle completo de un puesto de solo lectura desde el dashboard — `PuestosPage.tsx` solo muestra un resumen en la tabla, y "Editar" muestra todo en inputs editables, no como texto legible. Reusar la página pública `PuestoDetailPage.tsx` tal cual traería el botón "Postular a este puesto" a la vista del reclutador, que no tiene sentido — sería confuso, como si la app le sugiriera postularse a su propia oferta.

**Decisión 1 — extraer `Seccion` a un componente compartido, no duplicarlo:** hoy vive privado dentro de `PuestoDetailPage.tsx` (el helper que renderiza título+texto de cada bloque, y no renderiza nada si el texto viene vacío). Se mueve a `components/PuestoSeccion.tsx`, reusado por la página pública **y** por la vista nueva del dashboard — evita tener el mismo bloque de JSX en dos archivos.

**Decisión 2 — `Sheet` de shadcn, no `Dialog`:** el proyecto ya tiene `Sheet` instalado (lo usa el `Sidebar` responsive) y no tiene `Dialog` — un panel lateral además se siente más natural acá que un modal centrado, porque no tapa del todo la tabla de la que salió (mantiene el contexto de "estoy viendo mis puestos"). Se reusa el componente que ya existe en vez de instalar uno nuevo para esto.

**Decisión 3 — se abre con click en la fila, no con un botón nuevo:** la columna "Acciones" ya tiene "Editar" y "Cerrar puesto"/"Reabrir puesto" — agregar un tercer botón la satura. En cambio, click en cualquier parte de la fila (con `cursor-pointer`) abre el `Sheet` de detalle; los botones de acción existentes cortan la propagación del click (`event.stopPropagation()`) para no disparar el Sheet sin querer al usarlos.

- [x] 6.7.1 Frontend: extraído `PuestoSeccion` (antes `Seccion`, privado de `PuestoDetailPage.tsx`) a `components/PuestoSeccion.tsx`, y `MODALIDAD_LABEL` a `lib/puesto.ts` (estaba duplicado entre `PuestoDetailPage.tsx` y `PuestoFormPage.tsx` — se aprovechó para unificarlo en un solo lugar). `PuestoDetailPage.tsx` actualizado para importar ambos.
- [x] 6.7.2 Frontend: `PuestoDetailSheet.tsx` — `Sheet`/`SheetContent`/`SheetHeader`/`SheetTitle` de shadcn. Muestra título, badges de estado/modalidad/categoría, y las 4 secciones vía `PuestoSeccion` — sin botón de postular ni de editar.
- [x] 6.7.3 Frontend: `PuestosPage.tsx` — `onClick` en cada `TableRow` (`cursor-pointer`) abre `PuestoDetailSheet` con el puesto de esa fila; la celda de "Acciones" corta la propagación en un solo `onClick` (`event.stopPropagation()`) en vez de repetirlo en cada botón.
- [x] 6.7.4 Verificado en el navegador: click en la fila abre el Sheet con título, badges y las 4 secciones correctas; click en "Editar"/"Cerrar puesto"/"Reabrir puesto" no abre el Sheet.

_Frontend 6.7 completo — el reclutador ya tiene una vista de solo lectura del puesto sin salir del dashboard ni ver el CTA de postular pensado para candidatos._

### Backend 9.12 + Frontend 6.8 + Frontend 7.7: paginación en los listados que pueden crecer sin límite (agregado 2026-08-25)

**Contexto:** ninguno de los listados del proyecto está paginado — `REST_FRAMEWORK` en `settings.py` nunca tuvo `DEFAULT_PAGINATION_CLASS`. `/api/puestos/` (grilla pública de `ApplyPage` y `?mias=true` del dashboard), `/api/puestos/?mias=true` y `/api/postulaciones/` devuelven **todos** los registros en una sola respuesta, y el frontend renderiza todo lo que llega sin ningún control de página. No rompe con la cantidad de datos de hoy (decenas de puestos de prueba), pero degrada gradualmente con más volumen: la query de `PuestoViewSet` ya anota `postulaciones_count`/`preseleccionados` con `Count` (subqueries) por cada fila, y `ApplyPage`/`PuestosPage`/`PostulacionesPage` se convierten en una grilla/tabla cada vez más larga y pesada de renderizar.

**Decisión 1 — `PageNumberPagination` de DRF, no cursor ni limit-offset.** Da `?page=N` y una respuesta `{count, next, previous, results}` — el patrón más simple para una UX de "página X de Y", que es exactamente lo que hace falta acá. `CursorPagination` es para feeds tipo red social (orden estable bajo escrituras concurrentes), no para esto; `LimitOffsetPagination` no aporta nada extra sobre `PageNumberPagination` para este caso y es menos directo de consumir del lado del frontend.

**Decisión 2 — `pagination_class` explícito por `ViewSet`, no `DEFAULT_PAGINATION_CLASS` global.** Si se setea globalmente, **también paginaría `CategoriaViewSet`** sin querer — su listado se consume hoy como array plano en `fetchCategorias()` para el `<Select>` de categorías de `ApplyPage` y `PuestoFormPage`; paginarlo rompería esos dos lugares en silencio (el frontend intentaría iterar `{count, results}` como si fuera un array). Se declara `pagination_class` solo en `PuestoViewSet` y `PostulacionViewSet` — `CategoriaViewSet` se queda sin tocar a propósito, un catálogo chico y estable no necesita paginarse.

**Decisión 3 — un solo tamaño de página (12) y un componente de paginación compartido, no tres implementaciones sueltas.** Se instala `Pagination` de shadcn (`npx shadcn@latest add pagination`) y se envuelve en `components/PaginationControls.tsx`, que recibe `{count, next, previous, page, onPageChange}` y renderiza "Anterior / Página X de Y / Siguiente" — reusado en `ApplyPage`, `PuestosPage` y `PostulacionesPage`. Anterior/Siguiente en vez de "cargar más": cambiar de página reemplaza los resultados actuales en vez de acumular una lista creciente en estado, más simple de mantener en los 3 lugares.

**Decisión 4 — el tipo de respuesta paginada se modela una sola vez.** `PaginatedResponse<T>` en `lib/api.ts` (`{count, next, previous, results: T[]}`), reusado por `fetchPuestosAbiertos`, `fetchMisPuestos` y `fetchMisPostulaciones` — las tres pasan a aceptar un `page` y devolver `PaginatedResponse<T>` en vez de `T[]` directo.

- [x] 9.12.1 Backend: `StandardResultsPagination(PageNumberPagination)` — `page_size = 12`, `page_size_query_param = "page_size"` (permite pedir más por página puntualmente si hiciera falta, sin forzarlo).
- [x] 9.12.2 Backend: `PuestoViewSet.pagination_class = StandardResultsPagination` — afecta tanto el listado público como `?mias=true` (comparten el mismo `get_queryset()`). **Hallazgo real al correr los tests:** el `.annotate()` con `Count()` de `get_queryset()` le hace perder a Django el ordenamiento implícito de `Meta.ordering` (`UnorderedObjectListWarning` de Django, no de DRF) — sin orden estable, la paginación puede repetir o saltear filas entre páginas. Se agregó `.order_by("-created_at")` explícito al final de `get_queryset()`.
- [x] 9.12.3 Backend: `PostulacionViewSet.pagination_class = StandardResultsPagination`.
- [x] 9.12.4 Backend: confirmado que `CategoriaViewSet` no se toca (Decisión 2) — sigue sin `pagination_class`, sigue devolviendo el array plano.
- [ ] 9.12.5 Frontend: `PaginatedResponse<T>` en `lib/api.ts`; `fetchPuestosAbiertos`, `fetchMisPuestos`, `fetchMisPostulaciones` actualizados para aceptar `page` y devolver `PaginatedResponse<T>`.
- [ ] 9.12.6 Frontend: instalar `Pagination` de shadcn; `components/PaginationControls.tsx` (Decisión 3).
- [ ] 9.12.7 Frontend: `ApplyPage.tsx` — estado `page`, `PaginationControls` debajo de la grilla; cambiar de categoría resetea `page` a 1 (si no, se puede quedar en una página que ya no existe para la categoría nueva).
- [ ] 9.12.8 Frontend: `PuestosPage.tsx` y `PostulacionesPage.tsx` — mismo patrón, `PaginationControls` debajo de la tabla.
- [x] 9.12.9 Tests backend: actualizados los 14 tests existentes que asumían un array plano en `/api/puestos/`/`/api/postulaciones/` para leer `response.json()["results"]`; nuevo `test_puesto_list_is_paginated_with_more_than_one_page` (13 puestos → página 1 con 12 + `next`, página 2 con 1 + `previous`, sin ids repetidos entre páginas); `test_anyone_can_list_categorias` con aserción explícita de regresión (`isinstance(response.json(), list)`) para la Decisión 2. 116/116 tests del backend pasando.
- [ ] 9.12.10 Verificación en el navegador: con más de 12 puestos (reusando los de prueba que ya hay + alguno extra si hace falta), confirmar los controles de paginación en `/`, `/dashboard` y `/dashboard/postulaciones`; cambiar de categoría en `/` vuelve a la página 1; el `<Select>` de categorías en `ApplyPage`/`PuestoFormPage` sigue funcionando sin romperse.

## Notas

- El orden entre tracks importa: cada paso del gateway/frontend depende de que exista el paso equivalente del backend (por eso las referencias cruzadas, ej. "Backend Fase 1.2").
- No hay que terminar un track completo antes de tocar el siguiente — se puede ir turnando (ej. Backend 0-1 → Gateway 0-1 → Frontend 0-1 → Backend 2 → ...), siempre que cada paso quede probado antes de avanzar.
- El README se actualiza (stack, cómo correrlo, demo) según se van cerrando fases, no al final.
- Cada fase que agregue lógica nueva (endpoint, servicio, tarea Celery) debería incluir su test correspondiente en el mismo paso — no se deja la escritura de tests para el final.
- Los tests de cada app viven junto a esa app (`apps/interviews/tests/`), no en una carpeta `tests/` separada en la raíz.
