# Interviewer AI

Entrevistador técnico con IA por voz: el usuario responde preguntas de programación hablando por el navegador, y un pipeline de IA (voz → texto → LLM → voz) lo evalúa y responde en tiempo real vía WebSockets.

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

> Estado: **El círculo completo de voz funciona de punta a punta, con memoria de conversación real y persistencia — y ahora también corre completo en Docker.** Hablás por el micrófono en el navegador → Frontend (React) → Gateway (Node/Socket.io) → Backend (Django/Celery) → Deepgram (STT) → DeepSeek (LLM, con el historial de la entrevista) → ElevenLabs (TTS) → la respuesta se reproduce sola, con voz, en el navegador. Todo vía Redis pub/sub (sin polling). Cada entrevista se guarda en Postgres, y hay una pantalla de feedback final. Los seis servicios (Postgres, Redis, backend, celery worker, gateway, frontend) están dockerizados y se levantan con un solo `docker compose up`. Falta: patrones Strategy/Adapter (Backend Fase 7) y despliegue en un servidor real (Infra Fase 2). Ver [docs/ROADMAP.md](docs/ROADMAP.md) para el detalle.

## Por qué este proyecto

Proyecto de portafolio pensado para demostrar WebSockets bidireccionales con datos binarios (audio), procesamiento asíncrono real (no solo `async def` decorativo), e integración de múltiples APIs externas (STT, LLM, TTS) detrás de una arquitectura desacoplada.

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
├── backend/               # Django + Celery + Dockerfile — Fases 0-6 completas (LLM, STT, TTS, persistencia y memoria de conversación)
├── ws-gateway/            # Node + Express + Socket.io + Dockerfile — Fases 0-4 completas (puente hacia Django, memoria de conversación por sesión)
└── frontend/              # React + TypeScript + Dockerfile — Fases 0-4 completas (entrevista completa: texto, voz y feedback final)
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

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisiones técnicas](docs/DECISIONS.md)
