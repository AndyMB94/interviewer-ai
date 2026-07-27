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

> Estado: en fase de diseño / arranque. Ver [docs/ROADMAP.md](docs/ROADMAP.md) para el progreso.

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

**IA / APIs externas** (proveedor exacto por definir, ver [docs/DECISIONS.md](docs/DECISIONS.md))
- Speech-to-Text (ej. Deepgram / Whisper API)
- LLM (ej. Claude / GPT) para generar y evaluar preguntas
- Text-to-Speech (ej. ElevenLabs)

## Estructura del repo

```
interviewer_ai/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md   # arquitectura, diagrama, patrones de diseño
│   ├── ROADMAP.md        # fases de desarrollo, backend, gateway y frontend
│   └── DECISIONS.md      # decisiones técnicas y por qué (ADRs cortos)
├── backend/               # Django + Celery (pendiente de crear)
├── ws-gateway/            # Node + Express + Socket.io (pendiente de crear)
└── frontend/              # React (pendiente de crear)
```

## Requisitos

- Python 3.12+
- Node.js 22+
- pnpm
- Docker + Docker Compose

## Cómo correrlo

_Pendiente — se documenta cuando exista el primer setup funcional (ver Fase 0 en el roadmap)._

Cada servicio (`backend/`, `ws-gateway/`, `frontend/`) tiene su propio `.env` (secretos, no se commitea) y un `.env.example` (plantilla, sí se commitea) — al clonar el repo hay que copiar cada `.env.example` a `.env` y llenar los valores.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisiones técnicas](docs/DECISIONS.md)
