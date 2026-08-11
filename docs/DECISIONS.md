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

## 2026-08-04 Contabo Cloud VPS 4 (Core) como servidor de despliegue

**Contexto:** para Infra Fase 2 hace falta un VPS real. Se evaluaron Contabo y Hostinger, y dentro de Contabo sus tres líneas: Core (recursos compartidos, más barato), Performance (CPUs AMD EPYC, para cargas más pesadas) y Max Performance/VDS (CPU y RAM dedicados, sin "vecinos ruidosos").

**Decisión:** Contabo **Core VPS 4** (4 vCPU, 8GB RAM, 100GB SSD, ~$5.50/mes, plan mensual sin permanencia, imagen Ubuntu 24.04, sin Auto Backup). Suficiente de sobra para correr los 6 contenedores de este proyecto con tráfico de demo/portafolio.

**Alternativas consideradas:** Hostinger — virtualización KVM más estable y mejor soporte para stacks web tipo WordPress, pero Contabo da más RAM/almacenamiento por el mismo precio, lo cual pesa más para este caso de uso. Performance/Max Performance de Contabo — descartados por sobreingeniería: son para cargas de producción con tráfico real, no para un portafolio de demo. Auto Backup (+€1.65/mes) — descartado porque todo el código ya está en GitHub; lo único que se perdería sin backup es la base de datos de Postgres con las entrevistas de prueba, aceptable para este alcance.

**Nota operativa:** Contabo pide verificación de identidad (documento + comprobante de domicilio) en pedidos nuevos como medida antifraude — el aprovisionamiento del VPS quedó pausado unas horas hasta que se revisaron los documentos. Es una práctica conocida de este proveedor específico, no un error en la compra.

---

## 2026-08-05 Dominio `.dev` (Porkbun) + Nginx como proxy único delante de los 6 contenedores

**Contexto:** para HTTPS real (necesario porque el navegador bloquea `getUserMedia` fuera de un contexto seguro) hace falta un dominio — Let's Encrypt no emite certificados para una IP pelada. También había que decidir cómo exponer los 3 puntos de entrada del stack (frontend, WebSocket del gateway, media de Django) sin mezclar HTTP y HTTPS (mixed content).

**Decisión:** dominio `andymallcco.dev` (Porkbun, ~$8.75 primer año), con el subdominio `interviewer.andymallcco.dev` para este proyecto (dejando el dominio raíz libre para un portafolio futuro). Nginx corre directo en el VPS (no dockerizado) como único punto de entrada en el puerto 443, con Certbot (`certbot --nginx`) manejando el certificado y su renovación automática. Nginx reenvía por `location`: `/` al frontend (puerto 8080), `/socket.io/` al gateway (puerto 3000, con headers de upgrade para WebSocket), y `/media/` a Django (puerto 8000) — todos publicados en `127.0.0.1` por docker-compose, nunca expuestos directo a internet salvo a través de Nginx.

**Alternativas consideradas:** TLD `.com`/`.org` — se prefirió `.dev` porque Google exige HTTPS en toda esa extensión (encaja con el objetivo) y Porkbun regala el certificado de Let's Encrypt con el registro. Certificado autofirmado (sin comprar dominio) — descartado por mostrar advertencias de "sitio no seguro" en el navegador, poco profesional para un portafolio. Dockerizar Nginx también — se dejó nativo en el host por simplicidad, ya que solo necesita hablarle a los puertos publicados de los otros contenedores vía `127.0.0.1`.

**Nota operativa:** tras activar HTTPS, `VITE_GATEWAY_URL` (frontend, build-time), `PUBLIC_DJANGO_URL` y `CORS_ORIGINS` (gateway, runtime) se actualizaron de `http://<IP>:<puerto>` a `https://interviewer.andymallcco.dev` (mismo origen para todo, sin puertos) — necesario porque una página servida por HTTPS no puede hablarle a recursos en HTTP plano (mixed content, bloqueado por el navegador).

---

## 2026-08-05 Tailwind CSS + shadcn/ui para el rediseño del frontend (Frontend P.3), sin Redux

**Contexto:** el frontend hasta ahora es un único `App.tsx` con CSS plano mínimo (Frontend Fase 0-4, foco en funcionalidad, no en diseño). Para el rediseño visual se evaluaron alternativas de estilos/componentes (Tailwind + shadcn/ui, PrimeReact, Material UI) y de manejo de estado (Redux).

**Decisión:** Tailwind CSS (utilidades de estilo) + shadcn/ui (componentes base copiados al proyecto, construidos sobre Radix UI) para el diseño visual. Sin librería de manejo de estado global (Redux, Zustand, etc.) — el estado actual (conexión de socket, respuesta, transcripción, permiso de micrófono) sigue viviendo en los hooks `useSocket`/`useMicrophone` con `useState`, sin necesidad real de un store global.

**Alternativas consideradas:** PrimeReact / Material UI — librerías de componentes completos y pre-diseñados (tablas, calendarios, formularios complejos); se descartaron por ser sobreingeniería para una app de una sola pantalla con pocos elementos de UI, y porque Tailwind+shadcn da más control real sobre el diseño (shadcn copia el código fuente del componente al proyecto, no queda atado a la API/versión de una dependencia externa). Redux — descartado porque el estado actual es chico y ya está bien organizado en hooks; agregar un store global sería boilerplate sin beneficio real a este tamaño de app.

**Nota de escalabilidad:** la estructura de `components/`/`hooks/` está pensada para extenderse con `pages/` + `react-router` el día que exista una fase de autenticación (login, dashboard) — no se crean esas carpetas de antemano por estar vacías hoy. Ver [docs/ARCHITECTURE.md](ARCHITECTURE.md).

---

## 2026-08-06 Pivote de producto: de práctica de entrevistas a plataforma de reclutamiento con IA

**Contexto:** al planificar cómo agregar autenticación, surgió que el alcance real deseado es mayor — no una simple casilla de login sobre la herramienta de práctica existente, sino un embudo de reclutamiento completo (puesto → postulación con CV → filtro con IA → cuenta automática solo si aprueba → entrevista → panel de reclutador).

**Decisión:** se adopta el pivote. El nombre del proyecto pasa a ser **Vacantia** (pendiente de aplicar en la documentación/dominio, no bloquea el desarrollo). El roadmap se reorganiza en Backend Fase 8-9, Gateway Fase 5 y Frontend Fase 5-6 (ver ROADMAP.md) para reflejarlo.

**Alternativas consideradas:** mantener el alcance original (solo agregar login a la práctica de entrevistas) — descartada porque el usuario prefirió explícitamente el alcance mayor, con mejor visibilidad como pieza de portafolio.

---

## 2026-08-06 Autenticación híbrida (JWT en memoria + refresh token en cookie httpOnly), sin autoregistro

**Contexto:** con el pivote a plataforma de reclutamiento, el sistema empieza a manejar datos sensibles (documento de identidad, nacionalidad, resultados de entrevistas) — el nivel de seguridad de la autenticación importa más que en la versión anterior, más simple.

**Decisión:**
- Autenticación híbrida: un JWT de acceso de vida corta (guardado en memoria del lado del cliente, nunca en `localStorage`) más un refresh token en una cookie `httpOnly` (inaccesible para JavaScript, mitiga robo por XSS). El JWT de acceso viaja como header `Authorization` a través de la cadena React → gateway Node → Django.
- **Sin autoregistro de ningún tipo.** El Postulante nunca llena un formulario de "crear cuenta" — su cuenta nace automáticamente si su CV aprueba el filtro (Backend Fase 9.4). Reclutador/Administrador se crean a mano desde el admin de Django — nunca por un formulario público.
- `AUTH_USER_MODEL` se queda en el `User` default de Django — Groups (`Administrador`/`Reclutador`/`Postulante`) más un modelo `ApplicantProfile` uno-a-uno cubren roles y datos extendidos sin el riesgo de una migración irreversible de cambiar el modelo de usuario.

**Alternativas consideradas:** sesión pura de Django (cookie de sesión) — más simple de implementar, pero incómoda de propagar a través del gateway Node hacia Django sin plomería adicional. JWT puro guardado en `localStorage` — más simple todavía, pero vulnerable a robo del token vía XSS, un riesgo mayor ahora que se manejan datos sensibles. Un modelo de usuario custom (`AUTH_USER_MODEL` propio) — descartado por el riesgo de una migración irreversible sin necesidad real (Groups + perfil separado alcanza).

---

## 2026-08-06 Datos del postulante: qué se guarda y qué no, y por qué

**Contexto:** al diseñar `ApplicantProfile`, surgió la duda de qué datos personales del postulante guardar (documento, nacionalidad, fecha de nacimiento, sexo) y si debían usarse como criterio de filtro.

**Decisión:** se guardan tipo y número de documento (con tipo flexible: DNI / Carné de Extranjería / Pasaporte, para cubrir postulantes extranjeros), nacionalidad, fecha de nacimiento, sexo y teléfono — son datos habituales en un CV peruano y sirven para elegibilidad legal de trabajo y estadísticas agregadas. **Ninguno de estos se usa como criterio de descarte automático en el filtro de CVs** — el filtro con IA (Backend Fase 9.3) evalúa exclusivamente el fit técnico/profesional contra el puesto. Esto es una práctica de contratación deliberada: usar edad o sexo en la etapa de filtro es una fuente conocida de discriminación (consciente o no), por eso se excluyen de esa lógica aunque se almacenen.

**Alternativas consideradas:** no guardar estos datos en absoluto — descartado porque nacionalidad/documento sí son necesarios para elegibilidad legal real, y son datos estándar en el mercado peruano (a diferencia de mercados donde se evita pedirlos). Guardar también DNI/nacionalidad extraídos automáticamente vía una consulta a RENIEC/SUNAT — descartado explícitamente: no aporta nada a evaluar si alguien programa bien, y es un dato sensible innecesario sin beneficio real para el producto.

---

## 2026-08-06 Ubigeos vía API externa cacheada, no tabla propia con datos semilla

**Contexto:** para que el postulante seleccione su dirección (departamento/provincia/distrito) de una lista en vez de texto libre, se evaluó mantener una tabla propia con los ~1800 distritos del Perú (requiere conseguir e importar el dataset del INEI) vs. consumir una API externa.

**Decisión:** se usa `free.e-api.net.pe/ubigeos.json` como fuente (devuelve el árbol completo departamento→provincia→distrito en una sola respuesta, apto para armar el dropdown en cascada) — pero **no se le pega en vivo en cada request**: el backend la trae una vez y la cachea (el dato prácticamente no cambia), exponiendo su propio endpoint (`/api/accounts/ubigeo/...`) para que el frontend nunca dependa directamente del proveedor externo ni sepa cuál es.

**Alternativas consideradas:** tabla propia con datos semilla (fixture de Django) — técnicamente más robusta (sin dependencia externa), pero el usuario prefirió evitar el trabajo manual de conseguir/mantener ese dataset. `api.migo.pe` — descartada para este uso porque resuelve el caso inverso (dado un código de ubigeo ya conocido, devuelve su nombre), no sirve para poblar una lista de selección; además requiere token/registro.

---

## 2026-08-06 Filtro de CVs reutilizando el LLM existente, sin API paga de parseo

**Contexto:** para evaluar si un CV encaja con un puesto (Backend Fase 9.3), se evaluó contratar una API de parseo de CVs tipo ATS (Affinda, Sovren) vs. reutilizar la integración de LLM que ya existe en el proyecto.

**Decisión:** se extrae el texto plano del PDF con una librería simple (`pypdf`), y se le pasa ese texto + la descripción del puesto al LLM ya integrado (`LLMProvider`/`DeepSeekLLM`, patrón Strategy/Adapter existente desde Backend Fase 7) para que evalúe el fit — sin agregar ningún patrón de diseño nuevo, es un uso nuevo de algo que ya existe.

**Alternativas consideradas:** API paga de parseo de CV tipo ATS — descartada por costo y porque el LLM que ya está integrado resuelve el mismo problema (entender el contenido de un CV) sin sumar un servicio nuevo ni gastar de más.

---

## 2026-08-10 `LLMProvider.ask()` acepta un `system_prompt` opcional (Backend Fase 9.3)

**Contexto:** el filtro de CVs (Fase 9.3) necesita usar el mismo LLM (DeepSeek) que la entrevista, pero para una tarea completamente distinta (evaluar un CV contra un puesto, no entrevistar) — con un system prompt propio. La interfaz `DeepSeekLLM.ask()` tenía el system prompt de la entrevistadora ("Gaby") hardcodeado adentro, sin forma de usar otro.

**Decisión:** se agregó un parámetro opcional `system_prompt: str | None = None` a `LLMProvider.ask()` (interfaz) y `DeepSeekLLM.ask()` (implementación). Si no se pasa nada, usa el prompt de entrevista de siempre (`INTERVIEW_SYSTEM_PROMPT`, renombrado desde `SYSTEM_PROMPT` para dejar claro que es solo el de la entrevista) — así `apps/interviews/tasks.py` no necesitó ningún cambio. El filtro de CVs (`apps/recruiting/services/cv_screening_service.py`) pasa su propio `SCREENING_SYSTEM_PROMPT`, pidiéndole al LLM una respuesta en JSON estructurado (`{"decision": ..., "razon": ...}`) para poder parsearla de forma confiable.

**Alternativas consideradas:** crear una clase `LLMProvider` nueva/paralela solo para screening — descartada, sería duplicar toda la lógica de llamar a la API de DeepSeek por una diferencia de una sola línea (el system prompt). Este enfoque es el ejemplo de libro de extender una interfaz sin romper a quien ya la usa (principio abierto/cerrado).

---

## 2026-08-11 Resend (vía `django-anymail`) como proveedor de email transaccional

**Contexto:** Backend Fase 9.4 necesita mandar las credenciales generadas al postulante aprobado. Se evaluó Resend, SendGrid y Amazon SES.

**Decisión:** Resend, integrado con `django-anymail[resend]` — reemplaza el `EMAIL_BACKEND` de Django para que `django.core.mail.send_mail`/`EmailMessage` (la API estándar de Django) hablen con Resend, sin aprender un SDK nuevo. Referencia completa copiada en `docs/Email/Resend/`. Mientras no se verifique un dominio propio, se manda desde el dominio de test de Resend (`onboarding@resend.dev`), que solo entrega a la dirección con la que se creó la cuenta — suficiente para desarrollo, hay que verificar un dominio propio antes de producción real.

**Alternativas consideradas:** SendGrid y Amazon SES — ambos con tier gratuito, pero Resend se eligió por API/SDK más simple y por integrarse directo con la API de envío de emails que Django ya trae (vía Anymail), sin sumar conceptos nuevos al proyecto.

---

## 2026-08-11 Creación automática de cuenta al aprobar: unificar alta y reseteo de contraseña (Backend Fase 9.4)

**Contexto:** cuando una `Postulacion` se aprueba, hay que crear la cuenta del postulante. Pero el mismo email puede aprobar más de una vez (postula a un puesto, después a otro) — si ya existe una cuenta de una aprobación anterior, ¿qué pasa si el postulante no se acuerda de esa contraseña (pudieron pasar meses o años)?

**Decisión:** `provision_applicant_account()` (`apps/accounts/services/account_provisioning.py`) no distingue "crear" de "resetear" — siempre genera una contraseña temporal nueva y la aplica (`user.set_password()`), sea que el `User` se acabe de crear o ya existiera (`get_or_create` por `username=email`, ya que `username` es único a nivel de base en el modelo default de Django, a diferencia de `email`). El email de credenciales se manda siempre con la contraseña vigente en ese momento. Esto evita construir un flujo de "recuperar contraseña" para este caso — cada aprobación *es*, en la práctica, un reset, y como estas cuentas solo sirven para hacer la entrevista (sin otro estado que perder), invalidar la contraseña anterior no tiene costo real.

**Alternativas consideradas:** reusar la cuenta sin tocar la contraseña si ya existía — más simple, pero deja al postulante sin poder entrar si no recuerda la contraseña vieja, sin ninguna forma de recuperarla (no hay flujo de "olvidé mi contraseña" en el proyecto). Crear una cuenta nueva cada vez — descartado, generaría usernames duplicados (mismo email) y viola la unicidad de `username`.

---

## 2026-08-11 `Interview` se conecta al usuario autenticado sin cerrar el acceso anónimo todavía (Backend Fase 9.5)

**Contexto:** con Fase 8 (auth) y 9.4 (cuentas automáticas) ya andando, correspondía que `Interview.user` dejara de ser siempre `None`. Pero la demo pública en producción (`interviewer.andymallcco.dev`) sigue activa y sin login — ni el gateway reenvía el JWT (Gateway Fase 5.1, pendiente) ni el frontend tiene pantalla de login (Frontend Fase 5, pendiente).

**Decisión:** `/api/ask/` (`apps/interviews/views.py`) sigue siendo `AllowAny` — si llega un JWT válido, la `Interview` nueva se crea con `user=request.user`; si no, se crea con `user=None` como hasta ahora. No se exige autenticación todavía. El cierre real (bloquear el acceso anónimo) se hace recién en Frontend Fase 5.4, cuando el flujo completo de login ya esté listo del otro lado — así nunca queda la demo pública rota a mitad de camino.

**Alternativas consideradas:** exigir `IsAuthenticated` ya mismo — más "correcto" en el papel, pero rompía la demo en producción de inmediato sin ninguna alternativa funcional hasta terminar Gateway 5.1 + Frontend 5, violando el criterio del proyecto de no dejar nada roto entre pasos.

---

## 2026-08-11 Cierre del acceso anónimo a la entrevista (Gateway Fase 5.1 + Frontend Fase 5.4)

**Contexto:** en Backend Fase 9.5 se decidió no exigir login todavía porque el gateway no reenviaba el JWT y el frontend no tenía login — cerrar el acceso en ese momento hubiera roto la demo pública sin alternativa. Con Frontend 5.1-5.3 y Gateway 5.1 ya listos, llegó el momento coordinado de cerrar.

**Decisión:** el cliente manda el access token en el handshake de Socket.io (`io(URL, { auth: { token } })`); el gateway lo lee de `socket.handshake.auth.token` y lo reenvía como header `Authorization: Bearer <token>` solo en la llamada a `/api/ask/` (la única que usa `request.user`, ver Fase 9.5 — `transcribe`/`speak` no lo necesitan). Del lado del frontend, `RequireAuth` (wrapper de ruta) redirige a `/login` si no hay `accessToken` en el `AuthContext`, cerrando la ruta `/` a usuarios no autenticados. Confirmado end-to-end: login → chat funciona → la `Interview` creada queda con el `user` correcto en el admin.

**Costo conocido, no resuelto todavía:** el access token vive solo en memoria (`AuthContext`, nunca `localStorage`, decisión de Fase 8) — al refrescar la página se pierde y hay que volver a loguearse, aunque la cookie `httpOnly` con el refresh token (7 días) siga siendo válida. No se implementó un "silent refresh" al cargar la app (llamar a `/api/auth/token/refresh/` con la cookie para pedir un access token nuevo sin pedir credenciales) — queda como mejora de UX pendiente, no bloquea el flujo actual.

---

## 2026-08-11 Dominio propio verificado en Resend: `mail.andymallcco.dev`

**Contexto:** con el dominio de test de Resend (`onboarding@resend.dev`) solo se podía entregar al email de la cuenta de Resend — un candidato real con otro email nunca hubiera recibido sus credenciales. Era el bloqueante real para que Fase 9.4 sirviera en producción de verdad.

**Decisión:** se verificó `mail.andymallcco.dev` como subdominio dedicado a email (siguiendo la recomendación de Resend de no usar el dominio raíz, ver `docs/Email/Resend/add_a_domain.md`), agregando los registros DKIM (TXT) y SPF (MX + TXT) en Porkbun — verificación en Resend en menos de 15 minutos. `DEFAULT_FROM_EMAIL` (`backend/config/settings.py`) pasó de `onboarding@resend.dev` a `Vacantia <no-reply@mail.andymallcco.dev>`. Confirmado con un envío real a una casilla externa (no la cuenta de Resend), entregado sin marcarse como spam.

**Alternativas consideradas:** ninguna — era un paso obligatorio ya decidido de antemano (ver decisión del 2026-08-06 sobre ubigeos/proveedor de email), solo pendiente de ejecutar.

---

## Pendientes por decidir

_Ninguno por ahora — quedan proveedores de LLM, STT, TTS y email decididos. Ver arriba las notas de cada uno sobre posibles cambios futuros._
