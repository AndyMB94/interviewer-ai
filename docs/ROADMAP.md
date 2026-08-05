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

## Notas

- El orden entre tracks importa: cada paso del gateway/frontend depende de que exista el paso equivalente del backend (por eso las referencias cruzadas, ej. "Backend Fase 1.2").
- No hay que terminar un track completo antes de tocar el siguiente — se puede ir turnando (ej. Backend 0-1 → Gateway 0-1 → Frontend 0-1 → Backend 2 → ...), siempre que cada paso quede probado antes de avanzar.
- El README se actualiza (stack, cómo correrlo, demo) según se van cerrando fases, no al final.
- Cada fase que agregue lógica nueva (endpoint, servicio, tarea Celery) debería incluir su test correspondiente en el mismo paso — no se deja la escritura de tests para el final.
- Los tests de cada app viven junto a esa app (`apps/interviews/tests/`), no en una carpeta `tests/` separada en la raíz.
