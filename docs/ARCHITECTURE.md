# Arquitectura

## Vista general

Vacantia es una plataforma de reclutamiento con IA: un reclutador publica un puesto, un candidato postula con su CV sin necesitar cuenta, un filtro con IA evalúa el fit contra el puesto, y solo si aprueba se le crea una cuenta automáticamente (con sus credenciales por email) para que haga una entrevista de voz con IA contextualizada a ese puesto. El reclutador tiene su propio panel para ver sus puestos, sus postulaciones, y el detalle (transcripción + resultado del filtro) de cada entrevista.

```
Candidato                                   Reclutador
    │                                            │
    ▼                                            ▼
Postular con CV (sin cuenta)          Login (JWT híbrido, ver DECISIONS.md)
    │                                            │
    ▼                                            ▼
Filtro de CV con IA (Celery + LLM)    Panel: puestos, postulaciones,
    │                                  detalle de entrevista (transcripción +
    ├── rechaza → termina ahí          resultado del filtro de CV)
    │
    └── aprueba → se crea la cuenta + email de credenciales (Resend)
            │
            ▼
        Login (JWT en memoria + cookie httpOnly)
            │
            ▼
        Entrevista de voz con Gaby, contextualizada al puesto
        (o selector de puesto, si hay más de una postulación aprobada)
```

Auth híbrida (JWT de acceso en memoria del frontend + refresh token en cookie httpOnly), roles vía Django Groups (`Administrador`/`Reclutador`/`Postulante`), y sin autoregistro de ningún tipo — el detalle completo de estas decisiones está en `docs/DECISIONS.md`.

### El pipeline de audio de la entrevista

La pieza técnica más compleja del sistema es la entrevista de voz en sí — el resto del producto es CRUD + auth + un par de tareas Celery. Este es el pipeline en tiempo real detrás de esa parte:

```
Cliente (React)            WS Gateway (Node)                  Backend (Django)
┌─────────────────┐ WS  ┌────────────────────┐    REST  ┌──────────────────────────┐   APIs externas
│ Captura audio   │───▶│ Express + Socket.io │────────▶│ Encola tarea Celery      │
│ Reproduce audio │◀───│  (recibe/emite      │         │        │                  │
└─────────────────┘     │   audio por WS)    │          │        ▼                 │
                        │        ▲           │          │ Celery workers (Redis)   │
                        └────────│───────────┘          │        │                 │
                                 │   Redis pub/sub      │        ▼                 │
                                 └───────────────────── │ Capa de servicios (POO)  │──▶ STT / LLM / TTS
                                                        │ Interfaces STT, LLM y    │
                                                        │ TTS con adapters         │
                                                        └──────────────────────────┘
```

Flujo de una respuesta del usuario:

1. El cliente captura audio del micrófono y lo transmite por WebSocket (Socket.io) al **gateway Node**.
2. El gateway **no procesa nada** — reenvía el audio a Django vía un endpoint REST, que encola una tarea Celery. Esto mantiene al gateway liviano: solo mueve bytes, no espera respuestas lentas.
3. La tarea Celery usa la capa de servicios (en Django) para transcribir (STT), generar/evaluar con un LLM, y sintetizar la respuesta (TTS).
4. Cuando la tarea termina, Django publica el resultado en un canal de **Redis pub/sub** identificado por la sesión de entrevista.
5. El gateway Node está suscrito a ese canal; al recibir el mensaje, lo emite por el socket correcto al cliente.

## Por qué esta separación

- **Dos servicios, un solo broker (Redis) como puente.** Redis ya existía en el plan para Celery; se reutiliza como canal pub/sub para que Node y Django se hablen sin acoplarse directamente (Node nunca llama a Celery, ni Django conoce sockets).
- **El gateway no tiene lógica de negocio.** Solo enruta bytes de audio hacia adentro y eventos hacia afuera; toda la orquestación vive en Django (`services/`), donde es testeable sin necesitar una conexión WebSocket real.
- **Trade-off asumido:** dos lenguajes y dos procesos corriendo (Node + Django) en vez de uno solo. Se acepta esta complejidad adicional a cambio de usar Node/Socket.io para el canal en tiempo real.

## Patrones de diseño usados

### Strategy + Adapter (proveedores de IA)

Interfaz abstracta por tipo de proveedor (`STTProvider`, `LLMProvider`, `TTSProvider`), con una implementación concreta (adapter) por cada servicio externo:

```python
class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_chunk: bytes) -> str: ...

class DeepgramSTT(STTProvider):
    async def transcribe(self, audio_chunk: bytes) -> str:
        ...
```

Cada adapter traduce el formato específico de un proveedor externo a la interfaz interna uniforme. Cambiar de proveedor (ej. Deepgram → Whisper) no debería requerir tocar el resto del sistema — esto es inversión de dependencias (la "D" de SOLID).

### Observer / Pub-Sub (Redis pub/sub entre Node y Django)

El gateway Node se suscribe a un canal de Redis asociado a la sesión de entrevista. Cuando una tarea Celery (en Django) termina, publica el resultado a ese canal en vez de tener una referencia directa al socket del cliente — desacopla el trabajo pesado (Django/Celery) del canal en tiempo real (Node/Socket.io), que ni se conocen entre sí directamente.

### Command / State Machine (flujo de la entrevista)

Una entrevista tiene estados explícitos: `esperando_respuesta → transcribiendo → evaluando → generando_audio → esperando_respuesta`. Una clase `InterviewSession` valida las transiciones (ej. no se puede "evaluar" sin una transcripción lista).

### Repository (opcional)

Encapsula el acceso a datos vía Django ORM detrás de una interfaz, para que los servicios no dependan directamente del ORM y sean más fáciles de testear con mocks.

## Buenas prácticas a seguir

- **Composición sobre herencia:** el orquestador de la entrevista recibe (inyecta) sus providers en el constructor, no hereda de ellos.
- **Async real:** las tareas Celery que llaman a APIs externas usan clientes async (`httpx.AsyncClient` o SDKs async) en vez de bloquear un worker completo esperando la respuesta. Del lado de Node, los handlers de Socket.io son async por naturaleza (Node es single-threaded, event-driven) — no hay que "forzar" nada ahí.
- **DTOs tipados** (Pydantic o dataclasses) para pasar datos entre capas (audio recibido, transcripción, evaluación) en vez de diccionarios sueltos.
- **Tests con pytest + pytest-django**, colocados junto a cada app (`apps/interviews/tests/`). Gracias a Strategy/Adapter, el orquestador se testea con mocks de los providers, sin gastar en las APIs reales.

## Estructura de carpetas por servicio

### `backend/` (Django)

```
backend/
├── config/
│   ├── settings.py             # un solo archivo (dev y prod comparten config, ver .env)
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── interviews/
│   │   ├── models.py           # Interview (FK a Postulacion desde Fase 9.6, decision pendiente/avanza/no_avanza desde 9.10), Question, Answer
│   │   ├── views.py            # ask, health, transcribe, speak, finish_interview, interview_detail (9.8)
│   │   ├── permissions.py      # IsOwnerReclutadorOfInterview — solo el dueño del puesto ve la entrevista (9.8.2)
│   │   ├── urls.py
│   │   ├── tasks.py            # tareas Celery (ask_llm_task, transcribe_audio_task, synthesize_speech_task)
│   │   ├── tests/               # pytest, colocado con la app que prueba
│   │   └── services/            # lógica de negocio, NO en las vistas
│   │       └── interview_prompt_service.py  # arma el system_prompt contextual con el puesto (Fase 9.6.3)
│   ├── accounts/                # autenticación y roles (Backend Fase 8)
│   │   ├── models.py            # ApplicantProfile (perfil del postulante)
│   │   ├── views.py             # login/refresh/logout (JWT híbrido, ver DECISIONS.md)
│   │   ├── serializers.py       # CustomTokenObtainPairSerializer — agrega claims groups/email al JWT
│   │   ├── permissions.py       # IsAdministrador/IsReclutador/IsPostulante (por Django Group)
│   │   ├── admin.py
│   │   ├── migrations/          # incluye una migración de datos que crea los 3 Groups
│   │   ├── services/
│   │   │   ├── ubigeo_service.py        # trae y cachea departamento/provincia/distrito (Fase 8.4)
│   │   │   └── account_provisioning.py  # crea/resetea la cuenta del postulante aprobado + email de credenciales (Fase 9.4)
│   │   ├── templates/emails/
│   │   │   └── credenciales_postulante.html
│   │   └── tests/
│   └── recruiting/              # puestos y postulaciones (Backend Fase 9)
│       ├── models.py            # Puesto (9.1, categoria/funciones/requisitos_deseables/modalidad/vacantes desde 9.9-9.10), Postulacion (9.2), Categoria (tabla propia, seed vía migración de datos, 9.9)
│       ├── views.py             # PuestoViewSet, PostulacionViewSet, CategoriaViewSet (ReadOnly) + mi_postulacion (9.6.4, lista desde 9.7.2)
│       ├── permissions.py       # permisos a nivel de objeto (dueño del puesto)
│       ├── serializers.py       # PuestoSerializer (postulaciones_count, preseleccionados, categoria_nombre, vacantes), PostulacionSerializer (puesto_titulo, interview_id)
│       ├── tasks.py             # screen_postulacion_task (9.3)
│       ├── services/
│       │   ├── cv_screening_service.py  # extrae texto del CV y evalúa el fit con el LLM
│       │   └── postulacion_lookup.py    # get_ultima_postulacion_aprobada (9.6.2/9.6.4) y get_postulaciones_aprobadas_pendientes (9.7.1)
│       ├── admin.py
│       └── tests/
├── core/
│   └── ai_providers/            # adapters de proveedores externos (Fase 7, Strategy/Adapter)
│       ├── base.py              # interfaces abstractas (STTProvider, LLMProvider, TTSProvider...)
│       ├── deepgram_stt.py
│       ├── deepseek_llm.py
│       └── elevenlabs_tts.py
├── scripts/                     # scripts sueltos de validación, fuera de Django (uno por fase: "probar X en un script suelto")
│   ├── test_llm.py
│   ├── test_celery.py
│   ├── test_stt.py
│   └── test_tts.py
├── requirements.txt             # generado con `pip freeze` a medida que se instala
├── .env                         # secretos reales (SECRET_KEY, DB, Redis, API keys), gitignored
├── .env.example                 # plantilla sin valores, sí se commitea
└── manage.py
```

### `ws-gateway/` (Node + TypeScript + Express + Socket.io)

```
ws-gateway/
├── src/
│   ├── index.ts                # setup de Express + servidor Socket.io
│   ├── sockets/
│   │   └── interviewSocket.ts  # eventos del socket (ask, audio in, resultado out). Lee el JWT de
│   │                            # socket.handshake.auth.token (Gateway Fase 5.1). El postulacionId elegido
│   │                            # (Gateway 5.2) viaja como segundo argumento de los eventos ask/audio, NO en
│   │                            # el handshake — el socket se conecta al montar la página, antes de que la
│   │                            # persona elija en el selector (ver ROADMAP.md, Frontend 9.7.5/9.7.6).
│   └── services/
│       ├── djangoClient.ts     # llamadas REST al backend Django (askQuestion recibe postulacionId opcional)
│       └── redisSubscriber.ts  # suscripción a Redis pub/sub
├── package.json
├── tsconfig.json
├── .env                         # secretos reales, gitignored
└── .env.example                 # plantilla sin valores, sí se commitea
```

### `frontend/` (React + TypeScript)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                  # componentes de shadcn/ui (Button, Card, Table, Sidebar...), generados, no se editan a mano
│   │   ├── RootLayout.tsx       # Navbar + Outlet, envuelto en TooltipProvider (lo requiere Sidebar)
│   │   ├── Navbar.tsx           # toggle de tema, dropdown de cuenta/logout (P.5/P.6)
│   │   ├── DashboardLayout.tsx  # sidebar del panel de reclutador (Puestos/Postulaciones), Frontend 6.2
│   │   ├── QuestionDisplay.tsx  # transcripción en vivo (candidato), con avatares/timestamps
│   │   ├── MessageComposer.tsx  # composer de chat unificado (texto + mic, 3 estados), reemplaza VoiceRecorder/TextAnswerForm (P.10)
│   │   ├── PuestoCard.tsx       # tarjeta de un puesto en ApplyPage/PuestoDetailPage
│   │   ├── PuestoCardSkeleton.tsx
│   │   ├── RequireAuth.tsx      # wrapper de ruta: redirige a /login sin sesión (Frontend 5.4), espera el silent refresh (P.7)
│   │   └── RequireRole.tsx      # RequireAuth + chequeo de rol (claim `groups` del JWT), usado por /dashboard (6.1)
│   ├── hooks/
│   │   ├── useSocket.ts         # conexión socket.io-client; askQuestion/sendAudio reciben un postulacionId opcional (9.7.4)
│   │   ├── useMicrophone.ts     # permiso/grabación de audio del navegador
│   │   ├── useTheme.ts          # tema claro/oscuro manual, persistido en localStorage (P.6.1)
│   │   └── use-mobile.ts        # hook de shadcn (Sidebar responsive)
│   ├── pages/                   # una pantalla por archivo (Frontend Fase 5, react-router)
│   │   ├── InterviewPage.tsx    # sala de espera + selector de puesto si hay varias postulaciones pendientes (9.7.5/9.7.6) + chat, ruta /entrevista (protegida)
│   │   ├── ApplyPage.tsx        # postulación pública (elegir puesto + filtro por categoría), ruta / (7.1/7.5)
│   │   ├── PuestoDetailPage.tsx # detalle de un puesto + formulario de postulación con CV (9.9/7.5)
│   │   ├── LoginPage.tsx        # login (postulante o reclutador, redirige según rol), ruta /login
│   │   └── dashboard/           # panel de reclutador (Frontend Fase 6), rutas hijas de /dashboard
│   │       ├── PuestosPage.tsx           # tabla de puestos propios + vacantes/preseleccionados (6.2/9.10)
│   │       ├── PostulacionesPage.tsx     # tabla de postulaciones + botón "Ver entrevista" (6.2/6.3)
│   │       └── InterviewDetailPage.tsx   # transcripción + resultado del filtro de CV + decisión pendiente/avanza/no_avanza (6.3/6.4)
│   ├── context/
│   │   └── AuthContext.tsx      # access token en memoria (nunca localStorage) + silent refresh al montar (P.7)
│   ├── lib/
│   │   ├── utils.ts             # helper `cn()` de shadcn/ui
│   │   ├── jwt.ts               # decodeJwtPayload — lee roles/email del JWT sin librería externa
│   │   └── api.ts               # llamadas REST a Django (puestos, postulaciones, auth, entrevistas) — no pasan por el gateway
│   ├── router.tsx               # definición de rutas (createBrowserRouter)
│   └── main.tsx                 # AuthProvider + RouterProvider
├── public/
│   └── favicon.svg              # ícono propio de Vacantia (P.6.4)
├── components.json               # config de shadcn/ui
├── tailwind.config.js
├── package.json
├── tsconfig.json
├── .env                         # solo config pública (nunca secretos: se expone en el bundle)
└── .env.example
```

`pages/` + `react-router` ya están armados (Frontend Fase 5.1) — cada pantalla nueva se agrega como un archivo en `pages/` (o `pages/dashboard/` si es del panel de reclutador) más una entrada en `router.tsx`, sin tocar `components/`/`hooks/` (esos siguen siendo compartidos entre pantallas).

## Infraestructura (Docker)

Cada servicio propio (`backend/`, `ws-gateway/`, `frontend/`) tiene su propio `Dockerfile`. Un único `docker-compose.yml` en la raíz orquesta los seis servicios (`postgres`, `redis`, `backend`, `celery-worker`, `ws-gateway`, `frontend`) en una misma red de Compose:

- `backend` y `celery-worker` comparten la misma imagen (`build: ./backend`); solo cambia el `command:` de cada uno.
- Dentro de la red de Compose, los contenedores se resuelven por **nombre de servicio** (`postgres`, `redis`, `backend`), no por `localhost` — eso solo funciona para el navegador, que corre fuera de la red de Docker y accede por los puertos publicados al host.
- Volumen `postgres_data`: persiste los datos de Postgres entre reinicios de los contenedores.
- Volumen `media_data`, montado en `/app/media` tanto en `backend` como en `celery-worker`: sin él, el archivo de audio que genera la tarea de TTS (corrida por `celery-worker`) no sería visible para Django (`backend`), que es quien lo sirve al navegador — son contenedores con filesystems aislados aunque compartan imagen.

Ver [docs/DECISIONS.md](DECISIONS.md) para el detalle de estas decisiones (Infra Fase 1.4).

### Despliegue (Infra Fase 2)

En producción (VPS de Contabo), **Nginx corre nativo en el host** (no dockerizado) como único punto de entrada público, en el puerto 443 con HTTPS (certificado de Let's Encrypt vía Certbot, renovación automática). Los seis contenedores de Compose publican sus puertos solo en `127.0.0.1` (no expuestos directo a internet); Nginx reenvía cada tipo de tráfico según el `location`:

- `/` → `frontend` (puerto 8080)
- `/socket.io/` → `ws-gateway` (puerto 3000, con headers de upgrade para WebSocket)
- `/media/` → `backend` (puerto 8000, archivos de audio de TTS)
- `/api/` → `backend` (puerto 8000, postulación/login/dashboard le hablan a Django directo desde el navegador, no a través del gateway)
- `/admin/` → `backend` (puerto 8000, admin de Django)
- `/static/` → `alias /srv/vacantia-static/` (estáticos del admin/DRF, generados por `collectstatic` y servidos directo por Nginx, sin pasar por Django — ver Infra Fase 4 en ROADMAP.md)

El dominio (`vacantia.andymallcco.dev`) es obligatorio para el certificado real (Let's Encrypt no emite para una IP pelada) y para que el navegador permita `getUserMedia` (el micrófono no funciona fuera de un contexto seguro/HTTPS). Por esto, `VITE_GATEWAY_URL`/`VITE_API_URL` (frontend), `PUBLIC_DJANGO_URL` y `CORS_ORIGINS` (gateway) apuntan todos al mismo origen HTTPS del dominio en producción, en vez de a IPs/puertos sueltos — evita mezclar HTTP y HTTPS (mixed content), que el navegador bloquea. Ver [docs/DECISIONS.md](DECISIONS.md) (Infra Fase 2.3 y Fase 3).

**`frontend/nginx.conf`** (dentro de la imagen del contenedor `frontend`, distinto del Nginx del host): tiene `try_files $uri $uri/ /index.html`, necesario para que las rutas de React Router (`/postular`, `/login`) no den 404 al navegarlas directo o refrescar — la config default de `nginx:alpine` no tiene ese fallback.

## Modelo de datos

### `apps/interviews/models.py`

- **`Interview`**: una sesión de entrevista. `user` (`ForeignKey` nullable a `settings.AUTH_USER_MODEL` — `None` en las entrevistas anteriores a Backend Fase 8, o en la demo anónima que sigue funcionando), `postulacion` (`ForeignKey` nullable a `apps.recruiting.models.Postulacion`, agregado en Fase 9.6 — se conecta automáticamente a la `Postulacion` aprobada del usuario autenticado al crear la `Interview`, y es lo que le da a Gaby el contexto del puesto real para armar preguntas relevantes en vez de genéricas), `created_at`, `status` (`in_progress` / `finished`, vía `models.TextChoices`), `decision` (`pendiente` / `avanza` / `no_avanza`, vía `models.TextChoices`, agregado en 9.10 — decisión del reclutador tras revisar la entrevista; deliberadamente no `contratado`/`no_contratado`, ver DECISIONS.md: Vacantia cubre solo las primeras dos etapas de selección, no la entrevista técnica ni la decisión final de contratación).
- **`Question`**: cada mensaje del usuario (escrito o transcripto) dentro de una entrevista. `ForeignKey` a `Interview` (`related_name="questions"`), `text`, `created_at`.
- **`Answer`**: la respuesta del LLM a una pregunta puntual. `OneToOneField` a `Question` (`related_name="answer"`) — cada pregunta tiene exactamente una respuesta, nunca varias.

Ambas relaciones usan `on_delete=models.CASCADE`: borrar una `Interview` borra sus preguntas, borrar una `Question` borra su respuesta.

La memoria de conversación (Backend Fase 6.3) se arma consultando todas las `Question`/`Answer` anteriores de la misma `Interview` (ordenadas por `created_at`), y pasándoselas al LLM como historial antes de la pregunta nueva — así el entrevistador "recuerda" lo que ya se dijo en esa sesión.

### `apps/accounts/models.py`

- **`ApplicantProfile`**: `OneToOneField` a `settings.AUTH_USER_MODEL`. Datos del postulante que no viven en el `User` default de Django: `tipo_documento`/`numero_documento` (DNI, Carné de Extranjería o Pasaporte — `UniqueConstraint` sobre el par, ignorando filas en blanco), `nacionalidad`, `fecha_nacimiento`, `sexo`, `telefono`, y `ubigeo_codigo`/`departamento`/`provincia`/`distrito` como `CharField` planos (no `ForeignKey` — no hay tabla `Ubigeo` local, se resuelven contra el servicio cacheado de `services/ubigeo_service.py`, ver DECISIONS.md). No se crea automáticamente vía señal `post_save`: cada flujo de alta de cuenta decide si corresponde un perfil (a mano desde el admin para Reclutador/Administrador; automático y vacío al aprobar una `Postulacion`, Backend Fase 9.4 — el postulante lo completa después, en un paso de frontend todavía no construido).
- **Roles**: no hay un modelo propio — se usan los `Group` default de Django (`Administrador`/`Reclutador`/`Postulante`), creados por una migración de datos (`0002_create_groups.py`).

### `apps/recruiting/models.py`

- **`Puesto`**: `titulo`, `descripcion`, `requisitos`, `funciones`, `requisitos_deseables`, `modalidad` (`remoto`/`presencial`/`hibrido`), `vacantes` (entero, 9.10), `categoria` (`ForeignKey` a `Categoria`), `creado_por` (`ForeignKey` a `settings.AUTH_USER_MODEL`, siempre un usuario del Group `Reclutador`), `estado` (`abierto`/`cerrado`).
- **`Categoria`**: tabla propia (no `TextChoices`), `nombre` — sembrada por una migración de datos (mismo patrón que los Groups) para poder agregar categorías nuevas desde el admin sin deploy (ver DECISIONS.md, 9.9).
- **`Postulacion`**: `puesto` (`ForeignKey`, `related_name="postulaciones"`), `nombre`/`email` (el candidato todavía no tiene cuenta al postular), `cv` (`FileField`, valida extensión `.pdf`), `estado` (`pendiente`/`rechazado`/`aprobado`), `resultado_filtro` (texto libre con la razón que da el LLM). Se crea sin autenticación (endpoint público); al guardarse dispara `screen_postulacion_task` (Celery), que extrae el texto del CV y le pide al LLM que decida el fit contra el `Puesto` (Backend Fase 9.3).
