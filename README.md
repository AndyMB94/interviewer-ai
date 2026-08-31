# Vacantia

Plataforma de reclutamiento con IA: un reclutador publica un puesto, un candidato postula con su CV sin necesitar cuenta, un filtro con IA evalúa el fit contra el puesto, y si aprueba se le crea una cuenta automáticamente para que haga una entrevista técnica por voz con IA — contextualizada a ese puesto — vía WebSockets (voz → texto → LLM → voz, en tiempo real).

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Socket.io](https://img.shields.io/badge/Socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![pnpm](https://img.shields.io/badge/pnpm-F69220?style=for-the-badge&logo=pnpm&logoColor=white)

> Estado: **El embudo completo de reclutamiento está desplegado y funcionando en producción — [vacantia.andymallcco.dev](https://vacantia.andymallcco.dev)**. Un reclutador publica un puesto → un candidato postula con su CV sin necesitar cuenta → DeepSeek evalúa el fit contra el puesto → si aprueba, se crea la cuenta automáticamente y se manda la contraseña por email (Resend, dominio propio verificado) → el candidato inicia sesión (JWT en memoria + cookie httpOnly) → hace la entrevista de voz con Gaby, contextualizada al puesto real: Frontend (React) → Gateway (Node/Socket.io) → Backend (Django/Celery) → Deepgram (STT) → DeepSeek (LLM, con el historial de la entrevista) → ElevenLabs (TTS) → la respuesta se reproduce sola, con voz, en el navegador. Si tiene más de una postulación aprobada, elige para cuál puesto entrevistarse. El reclutador tiene su propio panel (login separado) para ver sus puestos, sus postulaciones, y el detalle de cada entrevista (transcripción + resultado del filtro de CV). Todo vía Redis pub/sub (sin polling), dockerizado detrás de Nginx + HTTPS en un VPS real. Ver [docs/ROADMAP.md](docs/ROADMAP.md) para el detalle completo y lo que sigue.

## Por qué este proyecto

Proyecto de portafolio pensado para demostrar, todo en un mismo sistema: WebSockets bidireccionales con datos binarios (audio), procesamiento asíncrono real (no solo `async def` decorativo), integración de múltiples APIs externas (STT, LLM, TTS) detrás de una arquitectura desacoplada, autenticación híbrida con roles (JWT + cookie httpOnly, Django Groups), un pipeline asíncrono de evaluación de candidatos con IA, y un panel multi-rol (candidato/reclutador) sobre la misma base de datos.

## Seguridad

- **Auth híbrida:** JWT de acceso en memoria del cliente (nunca `localStorage`) + refresh token en cookie `httpOnly` — un XSS no puede robar la sesión leyendo el DOM.
- **Permisos seguros por defecto:** cualquier endpoint nuevo que alguien se olvide de etiquetar queda protegido por error, no expuesto por error (`DEFAULT_PERMISSION_CLASSES: IsAuthenticated`, con `AllowAny` explícito solo donde corresponde).
- **Autenticación de servidor a servidor:** el canal de voz (transcripción/generación de audio) entre el gateway Node y el backend Django exige un secreto compartido propio, comparado a tiempo constante — nadie en internet puede pegarle directo a esos endpoints y gastar cuota de las APIs de IA sin pasar por una entrevista real.
- **Anti-abuso en Nginx:** límite de tasa por endpoint (más estricto en postulaciones y en `/admin/`), límite de tamaño de archivo, y páginas de error propias (429/413) con la identidad visual de la app en vez de las crudas de Nginx.
- **A nivel de datos:** un candidato no puede postular dos veces al mismo puesto con el mismo email; secretos (`SECRET_KEY`, credenciales de servicios) sin ningún valor por defecto — el sistema no arranca en silencio con una clave insegura.

Detalle técnico completo en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#seguridad).

## Stack

**Backend**
- Python / Django + DRF (lógica de negocio, API REST, auth, persistencia)
- Celery + Redis (tareas asíncronas: STT, LLM, TTS en background)
- PostgreSQL (persistencia de entrevistas)
- pytest + pytest-django (tests)

**WebSocket gateway**
- Node.js + TypeScript + Express + Socket.io (canal WebSocket, streaming de audio)
- Se comunica con el backend Django vía REST (para encolar trabajo) y con Celery vía Redis pub/sub (para recibir resultados)
- Gestor de paquetes: pnpm

**Frontend**
- React + TypeScript (cliente: captura de audio del micrófono, conexión WebSocket al gateway Node, reproducción de audio de respuesta)
- Gestor de paquetes: pnpm

**IA / APIs externas** (ver [docs/DECISIONS.md](docs/DECISIONS.md) para el porqué de cada elección)
- LLM: DeepSeek — genera y evalúa las respuestas
- Speech-to-Text: Deepgram — transcribe el audio del usuario
- Text-to-Speech: ElevenLabs — sintetiza la voz de las respuestas

## Estructura del repo

```
interviewer_ai/
├── README.md
├── docker-compose.yml     # los 6 servicios: postgres, redis, backend, celery-worker, ws-gateway, frontend
├── docs/
│   ├── ARCHITECTURE.md   # arquitectura, diagrama, patrones de diseño
│   ├── ROADMAP.md        # fases de desarrollo, backend, gateway y frontend
│   └── DECISIONS.md      # decisiones técnicas y por qué (ADRs cortos)
├── backend/               # Django + Celery + Dockerfile — Fases 0-7 completas (LLM, STT, TTS, persistencia, memoria de conversación y patrones Strategy/Adapter); Fase 8 (auth/roles, incluido el perfil del postulante) y Fase 9 (puestos/postulaciones, filtro de CV con IA, CRUD completo de puestos, panel de reclutador) completas
├── ws-gateway/            # Node + Express + Socket.io + Dockerfile — Fases 0-4 completas (puente hacia Django, memoria de conversación por sesión) + Fase 5 (JWT y postulación elegida hasta Django)
└── frontend/              # React + TypeScript + Dockerfile — Fases 0-7 completas (postulación pública, login, entrevista con selector de puesto, panel de reclutador con CRUD de puestos y detalle de entrevista, perfil del postulante) + mejoras de UX (P.1-P.12: rediseño visual, toasts, manejo de errores)
```

## Requisitos

- Python 3.12+
- Node.js 22+
- pnpm
- Docker + Docker Compose

## Cómo correrlo

Cada servicio tiene su propio `.env` (secretos, no se commitea) y un `.env.example` (plantilla, sí se commitea) — al clonar el repo hay que copiar `backend/.env.example` a `backend/.env` y completar los valores (API keys de DeepSeek/Deepgram/ElevenLabs, credenciales de Postgres que coincidan con `docker-compose.yml`).

### Opción A: todo en Docker

Desde la raíz del repo:
```bash
docker compose up --build -d
```

La primera vez (volumen de Postgres vacío) hay que aplicar las migraciones dentro del contenedor:
```bash
docker compose exec backend python manage.py migrate
```

Abrí `http://localhost:8080` en el navegador — ahí está el frontend, ya conectado al resto del stack dockerizado.

### Opción B: nativo (para desarrollo activo con recarga en caliente)

**1. Levantar Postgres y Redis** (desde la raíz del repo):
```bash
docker compose up -d postgres redis
```

**2. Backend** (desde `backend/`):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**3. Worker de Celery** (en otra terminal, mismo venv):
```bash
celery -A config worker --loglevel=info
```

Con esto disponibles: `/api/health/`, y los endpoints asíncronos `/api/ask/` (LLM), `/api/transcribe/` (STT), `/api/speak/` (TTS) — cada uno con el patrón `POST` (dispara la tarea, devuelve un `task_id`) + `GET .../<task_id>/` (consulta el resultado).

**4. Gateway** (en otra terminal, desde `ws-gateway/`):
```bash
pnpm install
pnpm run dev
```

**5. Frontend** (en otra terminal, desde `frontend/`):
```bash
pnpm install
pnpm run dev
```

Con todo esto corriendo, abrí `http://localhost:5173` en el navegador: podés escribir una pregunta de texto (respuesta del LLM en pantalla), o darle permiso al micrófono, grabar una pregunta hablada y detener — unos segundos después vas a escuchar la respuesta del entrevistador de IA, generada con voz real, de punta a punta (React → Socket.io → Django → Celery → Deepgram → DeepSeek → ElevenLabs → Redis pub/sub → de vuelta al navegador).

### Parar y reanudar

Para el día a día de desarrollo (con cualquiera de las dos opciones de arriba, o una mezcla de ambas), al terminar:

```bash
docker compose down
```

Para y borra los contenedores, pero no se pierde nada: `postgres_data` y `media_data` son volúmenes con nombre, sobreviven al `down` (la base de datos y los archivos subidos — CVs, audios de TTS — siguen ahí). Si además tenías algo corriendo nativo (`pnpm run dev`, `python manage.py runserver`, `celery worker`), basta con `Ctrl+C` en cada terminal — no tienen estado que perder.

Para retomar:

```bash
docker compose up -d
```

Sin `--build`, salvo que hayas hecho `git pull` o cambiado código del backend/gateway/frontend desde la última vez — en ese caso, `docker compose up -d --build`. Lo que hayas estado corriendo nativo (Opción B) se levanta de nuevo con los mismos comandos de la sección de arriba.

## Operación

Los 6 servicios escriben sus logs a stdout/stderr (no a archivos), como corresponde en Docker — no hay ninguna carpeta de logs en el repo ni en el servidor. Para diagnosticar cualquier problema, tanto en local como en producción (conectado por SSH al VPS):

```bash
docker compose ps                                    # estado de los 6 servicios
docker compose logs <servicio> --tail=50              # últimas líneas de un servicio
docker compose logs <servicio> -f                      # seguir los logs en vivo
docker compose up -d <servicio>                         # reiniciar un servicio puntual
```

Todos los servicios tienen `restart: unless-stopped` en `docker-compose.yml`, así que si un contenedor se cae por un error transitorio (ej. un corte breve de conexión a Redis), Docker lo reinicia solo — no debería hacer falta intervención manual salvo que el problema sea persistente.

### Datos de demo y reset completo

El comando `seed_puestos` siembra 31 puestos de ejemplo con contenido realista (distintas categorías, modalidades y niveles de seniority), pensado para que el catálogo público no se vea vacío ni con datos de prueba. Es idempotente (usa el título como clave, no duplica si ya corrió antes) y sirve tanto en local como en producción:

```bash
docker compose exec backend python manage.py seed_puestos --reclutador=<username-o-email-del-reclutador>
```

Cada puesto sembrado recibe un `límite_postulaciones` derivado de su propio título: los roles "— Sin Experiencia" (alta rotación) quedan en 100, los "— Senior" (nicho, especializados) en 15, y el resto en 50 (el default del modelo). Dos puestos (`Asistente Administrativo/a — Practicante` y `Community Manager — Junior`) se siembran ya con `estado="cerrado"`, para que el badge de "cerrado" del catálogo se vea sin tener que cerrar nada a mano.

Para empezar de cero por completo (borra toda la base de datos — usar con cuidado, sobre todo en producción):

```bash
docker compose down -v                                  # borra contenedores Y volúmenes (datos incluidos)
docker compose up -d --build                             # levanta todo de nuevo
docker compose exec backend python manage.py migrate     # crea el esquema en la base vacía

docker compose exec backend python manage.py createsuperuser
# usuario Administrador, para entrar a /admin/

docker compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User, Group
u = User.objects.create_user('reclutador', email='reclutador@ejemplo.com', password='CAMBIE-ESTA-PASSWORD')
u.groups.add(Group.objects.get(name='Reclutador'))
"
# cuenta Reclutador, para publicar/gestionar puestos

docker compose exec backend python manage.py seed_puestos --reclutador=reclutador@ejemplo.com
```

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisiones técnicas](docs/DECISIONS.md)
