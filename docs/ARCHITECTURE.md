# Arquitectura

## Vista general

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
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── interviews/
│   │   ├── models.py
│   │   ├── views.py          # endpoints REST (ask, health, subir audio)
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── tasks.py          # tareas Celery
│   │   ├── tests/            # pytest, colocado con la app que prueba
│   │   │   ├── test_views.py
│   │   │   └── test_services.py
│   │   └── services/         # lógica de negocio, NO en las vistas
│   │       ├── llm_service.py
│   │       ├── stt_service.py
│   │       ├── tts_service.py
│   │       └── interview_orchestrator.py
│   ├── accounts/             # autenticación y roles (Backend Fase 8)
│       ├── models.py          # ApplicantProfile (perfil del postulante)
│       ├── views.py           # login/refresh/logout (JWT híbrido, ver DECISIONS.md)
│       ├── permissions.py     # IsAdministrador/IsReclutador/IsPostulante (por Django Group)
│       ├── admin.py
│       ├── migrations/        # incluye una migración de datos que crea los 3 Groups
│       ├── services/
│       │   ├── ubigeo_service.py  # trae y cachea departamento/provincia/distrito (Fase 8.4)
│       │   └── account_provisioning.py  # crea/resetea la cuenta del postulante aprobado + email de credenciales (Fase 9.4)
│       ├── templates/emails/
│       │   └── credenciales_postulante.html
│       └── tests/
│   └── recruiting/            # puestos y postulaciones (Backend Fase 9)
│       ├── models.py          # Puesto (9.1), Postulacion (9.2)
│       ├── views.py           # PuestoViewSet, PostulacionViewSet (DRF ModelViewSet)
│       ├── permissions.py     # permisos a nivel de objeto (dueño del puesto)
│       ├── serializers.py
│       ├── tasks.py           # screen_postulacion_task (9.3)
│       ├── services/
│       │   └── cv_screening_service.py  # extrae texto del CV y evalúa el fit con el LLM
│       ├── admin.py
│       └── tests/
├── core/
│   └── ai_providers/          # adapters de proveedores externos (Fase 7, Strategy/Adapter)
│       ├── base.py            # interfaces abstractas (STTProvider, LLMProvider, TTSProvider...)
│       ├── deepgram_stt.py
│       ├── deepseek_llm.py
│       └── elevenlabs_tts.py
├── scripts/                    # scripts sueltos de validación, fuera de Django (uno por fase: "probar X en un script suelto")
│   ├── test_llm.py
│   ├── test_celery.py
│   ├── test_stt.py
│   └── test_tts.py
├── requirements.txt            # generado con `pip freeze` a medida que se instala
├── .env                        # secretos reales (SECRET_KEY, DB, Redis, API keys), gitignored
├── .env.example                # plantilla sin valores, sí se commitea
└── manage.py
```

Cuando el proyecto tenga settings reales de producción distintos a los de desarrollo, ahí sí conviene dividir en `requirements/base.txt` + `dev.txt` + `prod.txt` — no antes.

### `ws-gateway/` (Node + TypeScript + Express + Socket.io)

```
ws-gateway/
├── src/
│   ├── index.ts               # setup de Express + servidor Socket.io
│   ├── sockets/
│   │   └── interviewSocket.ts # eventos del socket (audio in, resultado out)
│   ├── services/
│   │   ├── djangoClient.ts    # llamadas REST al backend Django
│   │   └── redisSubscriber.ts # suscripción a Redis pub/sub
│   └── config/
│       └── env.ts
├── package.json
├── tsconfig.json
├── .env                        # secretos reales, gitignored
└── .env.example                # plantilla sin valores, sí se commitea
```

### `frontend/` (React + TypeScript)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                 # componentes de shadcn/ui (Button, Card...), generados, no se editan a mano
│   │   ├── Header.tsx
│   │   ├── QuestionDisplay.tsx
│   │   ├── VoiceRecorder.tsx
│   │   └── TextAnswerForm.tsx
│   ├── hooks/
│   │   ├── useSocket.ts        # conexión socket.io-client reutilizable
│   │   └── useMicrophone.ts    # permiso/grabación de audio del navegador
│   ├── pages/                  # una pantalla por archivo (Frontend Fase 5, react-router)
│   │   ├── InterviewPage.tsx   # la pantalla de entrevista original, sin cambios de comportamiento
│   │   └── ApplyPage.tsx       # postulación pública (elegir puesto + subir CV), ruta /postular
│   ├── lib/
│   │   ├── utils.ts            # helper `cn()` de shadcn/ui
│   │   └── api.ts              # llamadas REST a Django (puestos, postulaciones) — no pasan por el gateway
│   ├── router.tsx              # definición de rutas (createBrowserRouter)
│   └── main.tsx                # RouterProvider en vez de renderizar un solo componente
├── public/
├── components.json              # config de shadcn/ui
├── tailwind.config.js
├── package.json
├── tsconfig.json
├── .env                        # solo config pública (nunca secretos: se expone en el bundle)
└── .env.example
```

Estas estructuras son el objetivo a mediano plazo, no lo que se crea en la Fase 0 de cada track — al inicio cada carpeta va a estar casi vacía y se va llenando fase a fase (ver ROADMAP.md).

`pages/` + `react-router` ya están armados (Frontend Fase 5.1) — cada pantalla nueva (postulación, login, dashboard de reclutador) se agrega como un archivo en `pages/` más una entrada en `router.tsx`, sin tocar `components/`/`hooks/` (esos siguen siendo compartidos entre pantallas).

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

El dominio (`interviewer.andymallcco.dev`) es obligatorio para el certificado real (Let's Encrypt no emite para una IP pelada) y para que el navegador permita `getUserMedia` (el micrófono no funciona fuera de un contexto seguro/HTTPS). Por esto, `VITE_GATEWAY_URL` (frontend), `PUBLIC_DJANGO_URL` y `CORS_ORIGINS` (gateway) apuntan todos al mismo origen HTTPS del dominio en producción, en vez de a IPs/puertos sueltos — evita mezclar HTTP y HTTPS (mixed content), que el navegador bloquea. Ver [docs/DECISIONS.md](DECISIONS.md) (Infra Fase 2.3).

## Modelo de datos

### `apps/interviews/models.py`

- **`Interview`**: una sesión de entrevista. `user` (`ForeignKey` nullable a `settings.AUTH_USER_MODEL`), `created_at`, `status` (`in_progress` / `finished`, vía `models.TextChoices`). Queda `None` en todas las entrevistas anteriores a Backend Fase 8 (no existía autenticación) y va a seguir siendo `None` para cualquier entrevista que no venga de una `Postulacion` aprobada — Backend Fase 9.5 (futura) es la que lo completa, conectándolo a la `Postulacion` aprobada del candidato.
- **`Question`**: cada mensaje del usuario (escrito o transcripto) dentro de una entrevista. `ForeignKey` a `Interview` (`related_name="questions"`), `text`, `created_at`.
- **`Answer`**: la respuesta del LLM a una pregunta puntual. `OneToOneField` a `Question` (`related_name="answer"`) — cada pregunta tiene exactamente una respuesta, nunca varias.

Ambas relaciones usan `on_delete=models.CASCADE`: borrar una `Interview` borra sus preguntas, borrar una `Question` borra su respuesta.

La memoria de conversación (Backend Fase 6.3) se arma consultando todas las `Question`/`Answer` anteriores de la misma `Interview` (ordenadas por `created_at`), y pasándoselas al LLM como historial antes de la pregunta nueva — así el entrevistador "recuerda" lo que ya se dijo en esa sesión.

### `apps/accounts/models.py`

- **`ApplicantProfile`**: `OneToOneField` a `settings.AUTH_USER_MODEL`. Datos del postulante que no viven en el `User` default de Django: `tipo_documento`/`numero_documento` (DNI, Carné de Extranjería o Pasaporte — `UniqueConstraint` sobre el par, ignorando filas en blanco), `nacionalidad`, `fecha_nacimiento`, `sexo`, `telefono`, y `ubigeo_codigo`/`departamento`/`provincia`/`distrito` como `CharField` planos (no `ForeignKey` — no hay tabla `Ubigeo` local, se resuelven contra el servicio cacheado de `services/ubigeo_service.py`, ver DECISIONS.md). No se crea automáticamente vía señal `post_save`: cada flujo de alta de cuenta decide si corresponde un perfil (a mano desde el admin para Reclutador/Administrador; automático y vacío al aprobar una `Postulacion`, Backend Fase 9.4 — el postulante lo completa después, en un paso de frontend todavía no construido).
- **Roles**: no hay un modelo propio — se usan los `Group` default de Django (`Administrador`/`Reclutador`/`Postulante`), creados por una migración de datos (`0002_create_groups.py`).

### `apps/recruiting/models.py`

- **`Puesto`**: `titulo`, `descripcion`, `requisitos`, `creado_por` (`ForeignKey` a `settings.AUTH_USER_MODEL`, siempre un usuario del Group `Reclutador`), `estado` (`abierto`/`cerrado`).
- **`Postulacion`**: `puesto` (`ForeignKey`, `related_name="postulaciones"`), `nombre`/`email` (el candidato todavía no tiene cuenta al postular), `cv` (`FileField`, valida extensión `.pdf`), `estado` (`pendiente`/`rechazado`/`aprobado`), `resultado_filtro` (texto libre con la razón que da el LLM). Se crea sin autenticación (endpoint público); al guardarse dispara `screen_postulacion_task` (Celery), que extrae el texto del CV y le pide al LLM que decida el fit contra el `Puesto` (Backend Fase 9.3).
