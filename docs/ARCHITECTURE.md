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
│   └── accounts/             # auth (cuando se necesite)
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
│   │   ├── InterviewRoom.tsx
│   │   ├── AudioRecorder.tsx
│   │   └── AudioPlayer.tsx
│   ├── hooks/
│   │   └── useSocket.ts       # conexión socket.io-client reutilizable
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── tsconfig.json
├── .env                        # solo config pública (nunca secretos: se expone en el bundle)
└── .env.example
```

Estas estructuras son el objetivo a mediano plazo, no lo que se crea en la Fase 0 de cada track — al inicio cada carpeta va a estar casi vacía y se va llenando fase a fase (ver ROADMAP.md).

## Modelo de datos

_Pendiente — se documenta cuando se llegue a la fase de persistencia (ver ROADMAP.md, Backend Fase 6)._
