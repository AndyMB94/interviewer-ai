# Decisiones técnicas

Registro corto de decisiones y el porqué (ADRs breves). Se agrega una entrada cada vez que se elige entre alternativas reales, no de antemano.

## Formato

```
## [Fecha] Título de la decisión
**Contexto:** qué problema o disyuntiva había.
**Decisión:** qué se eligió.
**Alternativas consideradas:** qué más se evaluó y por qué no.
```

---

## 2026-07-27 Monorepo con backend/ y frontend/ separados

**Contexto:** el cliente necesita capturar audio del micrófono y manejar un WebSocket; se evaluó usar templates de Django o un frontend separado.

**Decisión:** React como frontend separado, en un monorepo (`backend/` + `frontend/`) en vez de dos repos distintos.

**Alternativas consideradas:** HTML + JS servido por Django (más simple, menos piezas, pero se descartó para mostrar un frontend moderno en el portafolio).

---

## 2026-07-27 Gateway WebSocket en Node.js en vez de Django Channels

**Contexto:** el canal WebSocket podía vivir dentro de Django (Channels, un solo servicio Python) o en un servicio separado en Node.

**Decisión:** Node.js + Express + Socket.io como gateway dedicado para el WebSocket, separado del backend Django. Node reenvía el audio a Django vía REST para encolar el trabajo pesado (Celery), y escucha los resultados por Redis pub/sub para emitirlos al cliente correcto.

**Alternativas consideradas:** Django Channels (todo en un solo servicio Python, sin necesidad de puente entre procesos) — más simple de mantener y desplegar, pero se descartó por preferencia explícita de usar Node.

**Costo asumido:** dos procesos y dos lenguajes corriendo (Node + Django) en vez de uno, y un mecanismo de comunicación entre ellos (REST + Redis pub/sub) que no existiría con Channels.

---

## 2026-07-27 TypeScript en frontend y ws-gateway

**Contexto:** el frontend (React) y el gateway (Node) se podían escribir en JavaScript plano o TypeScript.

**Decisión:** TypeScript en ambos. Se valora en portafolios profesionales y atrapa errores en tiempo de compilación en vez de en producción.

**Alternativas consideradas:** JavaScript plano — menos fricción inicial, pero se descartó porque el tipado aporta más de lo que cuesta configurar.

**Costo asumido:** una capa más de setup (`tsconfig.json`, tipos de las librerías) sobre todo lo demás que ya es nuevo (Socket.io, React, Celery).

---

## 2026-07-27 pnpm como gestor de paquetes

**Contexto:** npm viene preinstalado con Node y es el default; pnpm hay que instalarlo aparte pero es más rápido y eficiente en disco.

**Decisión:** pnpm para `frontend/` y `ws-gateway/`.

**Alternativas consideradas:** npm — cero setup extra, pero se descartó por preferencia explícita.

---

## 2026-07-27 Desarrollo local en WSL2, Docker Compose solo para infra al inicio

**Contexto:** la máquina de desarrollo es Windows con WSL2 (Ubuntu 24.04) disponible. Celery tiene soporte limitado en Windows nativo (depende de `fork()`, no disponible ahí).

**Decisión:** desarrollo dentro de WSL2, no en Windows nativo. Desde el inicio, un `docker-compose.yml` mínimo levanta solo Postgres y Redis; el resto del código (Django, Celery, Node, React) corre nativo (venv/pnpm) mientras se aprende cada framework. Dockerizar cada servicio propio (Dockerfiles + compose completo) se deja para una fase posterior, una vez que la funcionalidad ya esté probada.

**Alternativas consideradas:** Dockerizar todo desde el día 1 — se descartó porque suma una capa de aprendizaje (Docker) simultánea a Django/Celery/Node/React, justo lo que se quiere evitar (avanzar de a pasos chicos).

---

## 2026-07-27 Despliegue en VPS (Contabo/Hostinger) con Docker Compose

**Contexto:** el proyecto eventualmente se despliega en algún proveedor — se evaluó VPS simple (Contabo/Hostinger) vs AWS (ECS/Fargate).

**Decisión:** VPS + Docker Compose (`docker compose up -d` en el servidor, con Nginx de reverse proxy y SSL vía Let's Encrypt).

**Alternativas consideradas:** AWS con servicios administrados (ECS/Fargate, RDS, ElastiCache) — más impresionante para el CV si se quiere mostrar experiencia en AWS específicamente, pero es sobreingeniería para el alcance de este portafolio; se puede reconsiderar más adelante si el objetivo cambia.

## 2026-07-27 PostgreSQL desde el día 1, incluso en desarrollo local

**Contexto:** Postgres ya corre en Docker Compose desde Infra Fase 0.1 (el mismo paso que agrega Redis), así que en la práctica nunca hubo fricción de setup que resolver con una base de datos más liviana para desarrollo.

**Decisión:** PostgreSQL en todos los entornos, incluido desarrollo local, corriendo en Docker Compose desde el inicio. No se usa SQLite en ninguna etapa del proyecto.

**Alternativas consideradas:** SQLite para desarrollo rápido sin Docker — descartada porque no resuelve ninguna fricción real: Postgres ya corre en Docker desde el primer paso del roadmap (Infra Fase 0.1), así que no hay setup adicional que evitar.

---

## 2026-07-27 pytest + pytest-django sobre el test runner de Django

**Contexto:** Django trae su propio framework de tests basado en `unittest` (`manage.py test`); la alternativa es pytest + pytest-django.

**Decisión:** pytest + pytest-django — sintaxis más simple, mejores mensajes de error, fixtures reutilizables, es el estándar de facto en proyectos Django modernos.

**Alternativas consideradas:** `unittest` nativo de Django — no requiere instalar nada extra, pero se descartó por preferir la ergonomía de pytest.

---

## 2026-07-28 DeepSeek como proveedor de LLM inicial

**Contexto:** para Backend Fase 1 hace falta un proveedor de LLM. Se evaluaron Claude, GPT, Kimi y DeepSeek — el usuario no tenía cuenta creada en ninguno y quería empezar con algo barato para aprender la integración sin preocuparse por el costo.

**Decisión:** DeepSeek (modelo `deepseek-v4-flash` para desarrollo, el más económico de sus dos tiers) vía su API compatible con el SDK de OpenAI (`base_url: https://api.deepseek.com`). Documentación de referencia copiada en `docs/AI/DeepSeek/`.

**Alternativas consideradas:** Claude y GPT — mejor documentados y más reconocibles en un portafolio, pero se pospone por ahora a favor del costo mínimo de DeepSeek mientras se aprende la integración. Kimi — descartado por soporte/documentación en inglés más limitado para un primer uso.

**Nota:** no es una decisión cerrada — el usuario anticipa que más adelante podría migrarse a Claude o GPT. Gracias al patrón Strategy/Adapter ya planeado para `LLMProvider` (ver ARCHITECTURE.md, Fase 7 del roadmap), ese cambio futuro no debería requerir tocar el resto del sistema.

---

## 2026-07-30 Deepgram como proveedor de STT

**Contexto:** para Backend Fase 3 hace falta transcribir audio a texto. Se evaluaron Deepgram y Whisper API — según el roadmap actual (Frontend 2.3, Gateway 3.1, Backend 3.2), el audio siempre se graba completo y se manda entero, sin streaming en vivo.

**Decisión:** Deepgram (modelo `nova-3`, vía su SDK propio `deepgram-sdk`). Documentación de referencia en `docs/AI/Deepgram/STT.md`.

**Alternativas consideradas:** Whisper API — más simple y alcanza para el modelo actual "grabar completo y mandar" del roadmap, pero se prefirió Deepgram porque tiene soporte nativo de streaming en tiempo real, dejando la puerta abierta a agregar transcripción en vivo como mejora futura de portafolio (coherente con el objetivo del proyecto de mostrar WebSockets/tiempo real). Gracias al patrón Strategy/Adapter planeado (`STTProvider`, Fase 7), cambiar de proveedor más adelante no requeriría tocar el resto del sistema.

**Nota técnica:** el parámetro `language` es obligatorio pasarlo explícito (`language="es"` en este proyecto) — sin especificarlo, Deepgram asume inglés por defecto y la transcripción de audio en español falla silenciosamente (devuelve `transcript: ""` con `confidence: 0.0`, sin error).

---

## 2026-07-30 ElevenLabs como proveedor de TTS

**Contexto:** para Backend Fase 4 hace falta sintetizar voz a partir de texto. ElevenLabs era la opción de referencia desde el inicio del proyecto (ver README.md).

**Decisión:** ElevenLabs (SDK propio `elevenlabs`, modelo `eleven_v3`, voz de ejemplo `"George"`). Documentación de referencia en `docs/AI/ElevenLabs/TTS.md`.

**Alternativas consideradas:** no se evaluaron alternativas en profundidad — ElevenLabs es reconocido como el estándar de facto en naturalidad de voz, y el plan gratuito alcanzó sin problema para validar la integración.

**Nota técnica:** `text_to_speech.convert()` devuelve el audio en **streaming** (por chunks), no de una vez — hay que iterarlo y escribirlo a un archivo (`for chunk in audio: f.write(chunk)`), no asumir que devuelve los bytes completos directamente.

---

## 2026-08-04 URLs de servicios configurables por variable de entorno (Infra Fase 1.4)

**Contexto:** al integrar los seis servicios en un solo `docker-compose.yml`, el gateway (`ws-gateway`) tenía hardcodeados `http://localhost:8000` (Django) y `redis://localhost:6379` (Redis) desde las fases nativas. Dentro de la red de Docker Compose, cada contenedor debe resolver a otros por nombre de servicio (`backend`, `redis`), no por `localhost`.

**Decisión:** `DJANGO_URL` y `REDIS_URL` en `ws-gateway` ahora se leen de `process.env`, con el valor hardcodeado original como fallback (`process.env.DJANGO_URL || "http://localhost:8000"`), para que el mismo código sirva tanto en desarrollo nativo (sin esas variables seteadas) como en Docker Compose (donde se inyectan vía `environment:` apuntando a los nombres de servicio). La URL usada para construir el link de audio que consume el **navegador** (en `interviewSocket.ts`) se dejó fija en `http://localhost:8000`, porque el navegador corre fuera de la red de Docker y necesita el puerto mapeado al host, no el nombre interno del servicio.

**Alternativas consideradas:** ninguna — es el patrón estándar para que el mismo código corra nativo y dockerizado sin ramas de código distintas.

---

## 2026-08-04 Volumen compartido para archivos de media entre backend y celery-worker

**Contexto:** al dockerizar cada servicio por separado, `backend` y `celery-worker` pasaron a ser contenedores distintos con filesystems aislados (aunque comparten la misma imagen). La tarea de TTS corre en `celery-worker` y guarda el audio en `MEDIA_ROOT`, pero es `backend` (Django) quien lo sirve al navegador — sin compartir ese directorio, el archivo generado por uno no existía para el otro (`404 Not Found`).

**Decisión:** volumen nombrado `media_data`, montado en `/app/media` en ambos servicios dentro de `docker-compose.yml`.

**Alternativas consideradas:** ninguna evaluada en profundidad — es el mecanismo estándar de Docker Compose para compartir archivos entre contenedores.

---

## 2026-08-04 InterviewSession como máquina de estados independiente, sin conectar a las tareas Celery reales (Backend Fase 7.3)

**Contexto:** el roadmap pedía modelar `InterviewSession` con los estados `esperando_respuesta → transcribiendo → evaluando → generando_audio → esperando_respuesta`, validando transiciones. Hoy, `transcribe_audio_task`, `ask_llm_task` y `synthesize_speech_task` son 3 tareas Celery independientes, disparadas por 3 llamadas REST separadas que hace el gateway en secuencia — no hay un solo punto en Django que orqueste las tres y pueda usar esta máquina de estados sin persistir el estado entre requests.

**Decisión:** `InterviewSession` (en `core/interview_session.py`) se construyó y testeó como clase standalone, sin conectarla a las tareas reales — demuestra el patrón State/Command (ver ARCHITECTURE.md) sin cambiar el comportamiento del sistema, en línea con el encabezado de la Fase 7 ("refactor, sin funcionalidad nueva").

**Alternativas consideradas:** conectarla de verdad al flujo real (ej. agregar un campo de estado fino a `Interview` y validar en cada tarea) — se descartó para este paso porque implica persistir estado entre 3 requests HTTP independientes y decidir qué responder ante una transición inválida, que es funcionalidad nueva, no refactor. Queda como candidato natural para cuando se construya `interview_orchestrator.py` (ya previsto en ARCHITECTURE.md) si en el futuro se decide mover la orquestación de las 3 llamadas al lado de Django en vez del gateway.

---

## Pendientes por decidir

_Ninguno por ahora — quedan proveedores de LLM, STT y TTS decididos. Ver arriba las notas de cada uno sobre posibles cambios futuros._
