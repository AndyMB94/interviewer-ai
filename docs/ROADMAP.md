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
- [ ] P.5 Rediseño de las pantallas del candidato (agregado 2026-08-11, con el skill de shadcn/ui ya instalado — ver DECISIONS.md). Alcance: `/`, `/postular`, `/login`. **Sin sidebar acá** (sería sobreingeniería para pantallas de una sola tarea — el sidebar queda reservado para Frontend Fase 6, que sí tiene varias vistas).
  - [x] P.5.1 Navbar simple compartida entre las 3 pantallas (`RootLayout` + `Navbar`, layout route en `router.tsx`), con `DropdownMenu` de cuenta (avatar/email + "Cerrar sesión") cuando hay sesión activa — usa el endpoint `/api/auth/logout/` que ya existía desde Fase 8, solo faltaba conectarlo a la UI. `Header.tsx` (el `<h1>` viejo) se eliminó, reemplazado por la navbar. Probado end-to-end: navbar en las 3 pantallas, logout limpia la sesión de verdad (vuelve a pedir login).
  - [x] P.5.2 Mejorar los globos de chat en `QuestionDisplay` — avatar (`Avatar`/`AvatarFallback` de shadcn) con ícono de bot para Gaby y la inicial del email para el usuario, timestamp (`toLocaleTimeString`) debajo de cada mensaje, alineados con `items-start` (arriba, no abajo — se ve mejor con globos altos como los que tienen reproductor de audio).
  - [x] P.5.3 Pasada de responsive — verificado en Chrome DevTools (device toolbar, iPhone SE) en las 3 pantallas, sin superposiciones ni cortes. No hizo falta tocar código: los contenedores ya usaban `mx-auto max-w-*` + flex/grid sin anchos fijos en px, mobile-friendly desde el vamos.
- [ ] P.6 Más pulido visual (agregado 2026-08-11, tras revisar qué faltaba después de P.5). Alcance:
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

## Pivote: plataforma de reclutamiento con IA (agregado 2026-08-06, reemplaza la sección "Autenticación" anterior)

**Contexto:** el proyecto deja de ser solo una herramienta de práctica de entrevistas y pasa a ser un embudo de reclutamiento completo: una empresa publica un puesto, los candidatos postulan mandando su CV (sin cuenta todavía), un filtro con IA evalúa el fit contra el puesto, y **solo si aprueba** se le crea una cuenta automáticamente y se le mandan las credenciales por correo — recién ahí hace la entrevista de voz con la IA. Un reclutador tiene su propio panel para ver los postulantes de sus puestos y los resultados de sus entrevistas. Ver `docs/DECISIONS.md` para el detalle de cada decisión tomada acá.

**Nombre del proyecto:** se decidió renombrar a **Vacantia** (pendiente de aplicar en README/docs/dominio — se hace cuando se llegue a esa parte, no bloquea el trabajo de backend).

### Backend — Fase 8: Autenticación y roles (arranca ahora)

- [x] 8.1 Instalar `djangorestframework-simplejwt` + `django-cors-headers`; configurar autenticación híbrida (JWT de acceso en memoria del lado del cliente, refresh token en cookie `httpOnly`).
- [x] 8.2 Crear los 3 Groups de Django (`Administrador`, `Reclutador`, `Postulante`) vía migración de datos.
- [x] 8.3 Nueva app `apps/accounts`: modelo `ApplicantProfile` (uno a uno con el usuario — tipo y número de documento, nacionalidad, fecha de nacimiento, sexo, teléfono, departamento/provincia/distrito) + endpoints `login`/`refresh`/`logout`.
- [x] 8.4 Servicio de ubigeos (`departamento`/`provincia`/`distrito` seleccionables) consumiendo `free.e-api.net.pe/ubigeos.json` como fuente, cacheado del lado del backend (no se le pega en vivo por cada request) — el frontend consume un endpoint propio, no la API externa directo.

### Backend — Fase 9: Puestos y postulaciones (futura)

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

### Frontend — Fase 6: Panel de reclutador (futura)

**Diseño:** acá sí va sidebar (componente `Sidebar` de shadcn/ui) — a diferencia de las pantallas del candidato (ver P.5), el dashboard tiene varias vistas reales (puestos, postulaciones, detalle de entrevista) que se benefician de navegación lateral. Tablas con el componente `Table` de shadcn, `Badge` para los estados (pendiente/aprobado/rechazado, con color por estado), y algún gráfico simple (postulaciones por estado) con el componente `Chart` de shadcn si aporta valor real — no decorativo. **Nota (6.2):** se evaluó `@tanstack/react-table` para sorting/paginación pero la versión instalada (9.1.2) resultó ser una reescritura mayor con una API completamente distinta a la v8 estable documentada (no exporta `useReactTable`/`getCoreRowModel`/`flexRender`) — se descartó la dependencia y las tablas se renderizan con `.map()` plano sobre los primitivos `Table` de shadcn, ya que hoy no se usa sorting/paginación real. Si se necesita más adelante, reinstalar fijando `@tanstack/react-table@^8` explícitamente.

- [x] 6.1 Login de reclutador — reusa `LoginPage`/`AuthContext` que ya existen (mismo endpoint `/api/auth/login/`, no se duplica el mecanismo). El rol viaja como claim custom en el JWT (`CustomTokenObtainPairSerializer`, ver DECISIONS.md 2026-08-12) — `AuthContext` lo decodifica al loguear, `LoginPage` redirige a `/dashboard` (Reclutador) o `/entrevista` (Postulante); `/dashboard` protegida con `RequireRole` (extiende `RequireAuth`). Probado end-to-end con una cuenta de reclutador real: login → `/dashboard`; un Postulante no puede entrar a `/dashboard` a mano, y viceversa.
- [x] 6.2 Dashboard con sidebar (`DashboardLayout.tsx`, componente `Sidebar` de shadcn, nav "Puestos"/"Postulaciones"). Backend: `PuestoViewSet` soporta `?mias=true` (filtra por `creado_por`, `Puesto.objects.none()` si no autenticado) y anota `postulaciones_count` (`Count("postulaciones")`); `PostulacionViewSet` agrega `select_related("puesto")` y expone `puesto_titulo` (campo `source="puesto.titulo"`) para evitar joins del lado del cliente. Frontend: `PuestosPage.tsx` (tabla título/estado/cantidad de postulaciones) y `PostulacionesPage.tsx` (tabla nombre/email/puesto/estado con `Badge` por color). Tests: `test_mias_filter_returns_only_the_reclutador_own_puestos`, `test_mias_filter_returns_empty_for_anonymous`, `test_puesto_list_includes_postulaciones_count` en `apps/recruiting`. Probado en navegador con una cuenta de reclutador real.
- [x] 6.3 Vista de detalle de una entrevista completada (transcripción + resultado del filtro de CV), agregado 2026-08-12. Usa Backend 9.8 (`GET /api/interviews/<id>/` + `interview_id` en `PostulacionSerializer`).
  - [x] 6.3.1 Botón "Ver entrevista" en cada fila de `PostulacionesPage.tsx` — visible solo si `interview_id` no es `null`. Usa `Button` de shadcn con `render={<Link .../>}` + `nativeButton={false}` (Base UI exige avisar explícitamente cuando el botón renderiza como otro elemento, ej. un `<a>`, en vez de un `<button>` nativo).
  - [x] 6.3.2 Página nueva `pages/dashboard/InterviewDetailPage.tsx`, ruta `/dashboard/entrevistas/:id` (child de `DashboardLayout`, mismo `RequireRole` que el resto del panel) — muestra el resultado del filtro de CV (`resultado_filtro` + `Badge` de estado) y la transcripción completa (pregunta/respuesta en orden, versión de solo lectura, distinta del `QuestionDisplay` del candidato que depende del socket en vivo).
  - [x] 6.3.3 `fetchInterviewDetail(token, interviewId)` en `lib/api.ts`.

_9.8 + 6.3 probados end-to-end en local: reclutador dueño ve la transcripción completa de una postulación de prueba con entrevista finalizada._

### Backend 9.9 + Frontend 7.5: página de detalle de puesto, formato real de oferta, y categorías (agregado 2026-08-13, futura)

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

### Backend 9.10 + Frontend 6.4: avance a la siguiente etapa y vacantes por puesto (agregado 2026-08-13, futura — revisado el mismo día tras aclarar el alcance real del producto)

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

## Notas

- El orden entre tracks importa: cada paso del gateway/frontend depende de que exista el paso equivalente del backend (por eso las referencias cruzadas, ej. "Backend Fase 1.2").
- No hay que terminar un track completo antes de tocar el siguiente — se puede ir turnando (ej. Backend 0-1 → Gateway 0-1 → Frontend 0-1 → Backend 2 → ...), siempre que cada paso quede probado antes de avanzar.
- El README se actualiza (stack, cómo correrlo, demo) según se van cerrando fases, no al final.
- Cada fase que agregue lógica nueva (endpoint, servicio, tarea Celery) debería incluir su test correspondiente en el mismo paso — no se deja la escritura de tests para el final.
- Los tests de cada app viven junto a esa app (`apps/interviews/tests/`), no en una carpeta `tests/` separada en la raíz.
