from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from apps.recruiting.models import Categoria, Puesto

PUESTOS = [
    {
        "titulo": "Desarrollador/a Backend Python (Django) — Semi-Senior",
        "categoria": "Tecnología / Sistemas",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 2,
        "descripcion": (
            "🚀 Buscamos un/a Desarrollador/a Backend con sólido conocimiento de Python y "
            "Django para sumarse al equipo de producto. La persona seleccionada trabajará en "
            "el diseño de APIs REST, integración de servicios externos y optimización de "
            "consultas a base de datos, dentro de un equipo ágil orientado a resultados."
        ),
        "funciones": (
            "🔧 Diseñar y mantener APIs REST con Django REST Framework.\n"
            "🗄️ Modelar y optimizar la base de datos (PostgreSQL).\n"
            "⚙️ Integrar servicios de terceros (pasarelas de pago, mensajería, IA).\n"
            "✅ Escribir tests automatizados (pytest) para cada funcionalidad nueva.\n"
            "🤝 Participar en revisiones de código y ceremonias ágiles del equipo."
        ),
        "requisitos": (
            "📌 3+ años de experiencia con Python en entornos productivos.\n"
            "📌 Experiencia sólida con Django y Django REST Framework.\n"
            "📌 Manejo de PostgreSQL y control de versiones con Git.\n"
            "📌 Conocimientos de arquitectura de APIs REST."
        ),
        "requisitos_deseables": (
            "⭐ Experiencia con Celery y colas de tareas asíncronas.\n"
            "⭐ Conocimientos de Docker y despliegue en la nube.\n"
            "⭐ Inglés técnico para lectura de documentación."
        ),
    },
    {
        "titulo": "Desarrollador/a Frontend React — Junior",
        "categoria": "Tecnología / Sistemas",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 1,
        "descripcion": (
            "💻 ¡Es tu oportunidad para dar el salto profesional! Buscamos un/a "
            "Desarrollador/a Frontend Junior con ganas de crecer, para trabajar junto a un "
            "equipo senior en el desarrollo de interfaces modernas con React y TypeScript."
        ),
        "funciones": (
            "🎨 Construir componentes de interfaz reutilizables con React.\n"
            "🔗 Consumir APIs REST y manejar estado del lado del cliente.\n"
            "🐛 Detectar y corregir bugs de interfaz junto al equipo de QA.\n"
            "📱 Cuidar la responsividad y accesibilidad de las pantallas."
        ),
        "requisitos": (
            "📌 0-1 año de experiencia laboral o proyectos personales/académicos con React.\n"
            "📌 Conocimientos de HTML, CSS y JavaScript moderno (ES6+).\n"
            "📌 Nociones de control de versiones con Git.\n"
            "📌 Ganas de aprender y recibir feedback constante."
        ),
        "requisitos_deseables": (
            "⭐ Conocimientos de TypeScript.\n"
            "⭐ Familiaridad con Tailwind CSS u otro framework de estilos utilitario.\n"
            "⭐ Estudios en curso o egresado/a de Ingeniería de Sistemas o afines."
        ),
    },
    {
        "titulo": "DevOps / SRE Engineer — Senior",
        "categoria": "Tecnología / Sistemas",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 1,
        "descripcion": (
            "☁️ Empresa en expansión busca un/a Ingeniero/a DevOps Senior para liderar la "
            "confiabilidad y escalabilidad de la infraestructura en la nube, con foco en "
            "automatización, observabilidad y buenas prácticas de seguridad."
        ),
        "funciones": (
            "🐳 Administrar infraestructura containerizada (Docker/Kubernetes).\n"
            "🔄 Diseñar e implementar pipelines de CI/CD.\n"
            "📈 Definir métricas de observabilidad (logs, métricas, alertas).\n"
            "🔐 Auditar y reforzar la seguridad de los entornos productivos."
        ),
        "requisitos": (
            "📌 5+ años de experiencia en roles de DevOps/SRE/Infraestructura.\n"
            "📌 Experiencia sólida con Docker, Kubernetes y proveedores cloud (AWS/GCP/Azure).\n"
            "📌 Manejo de herramientas de CI/CD (GitHub Actions, GitLab CI o similares).\n"
            "📌 Scripting en Bash/Python para automatización."
        ),
        "requisitos_deseables": (
            "⭐ Certificaciones cloud (AWS/GCP).\n"
            "⭐ Experiencia con Terraform u otra herramienta de Infraestructura como Código.\n"
            "⭐ Inglés avanzado."
        ),
    },
    {
        "titulo": "Analista de Datos — Practicante",
        "categoria": "Análisis de Datos",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 2,
        "descripcion": (
            "📊 Programa de prácticas para estudiantes o recién egresados/as apasionados/as "
            "por los datos. La persona seleccionada apoyará al equipo de Análisis de Datos en "
            "la elaboración de reportes y visualizaciones para la toma de decisiones."
        ),
        "funciones": (
            "📥 Recolectar y limpiar datos de distintas fuentes internas.\n"
            "📊 Elaborar reportes y dashboards de seguimiento.\n"
            "🔍 Apoyar en el análisis exploratorio de datos para proyectos puntuales.\n"
            "🗣️ Comunicar hallazgos de forma clara al equipo."
        ),
        "requisitos": (
            "📌 Estudiante de últimos ciclos o egresado/a reciente de Ingeniería, Estadística, "
            "Economía o carreras afines.\n"
            "📌 Manejo de Excel a nivel intermedio-avanzado.\n"
            "📌 Nociones de SQL.\n"
            "📌 Disponibilidad para prácticas a tiempo completo."
        ),
        "requisitos_deseables": (
            "⭐ Conocimientos de Python (pandas) o Power BI.\n"
            "⭐ Cursos o certificaciones en análisis de datos."
        ),
    },
    {
        "titulo": "Data Scientist — Senior",
        "categoria": "Análisis de Datos",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 1,
        "descripcion": (
            "🤖 Buscamos un/a Data Scientist Senior para liderar el desarrollo de modelos "
            "predictivos que impacten directamente en las decisiones estratégicas del "
            "negocio, trabajando de la mano con equipos de producto e ingeniería."
        ),
        "funciones": (
            "🧠 Diseñar, entrenar y evaluar modelos de machine learning.\n"
            "🔬 Realizar experimentos A/B para validar hipótesis de negocio.\n"
            "🚀 Llevar modelos a producción junto al equipo de ingeniería.\n"
            "📚 Mentorear a analistas junior del equipo."
        ),
        "requisitos": (
            "📌 4+ años de experiencia en ciencia de datos o machine learning.\n"
            "📌 Dominio de Python (pandas, scikit-learn) y SQL.\n"
            "📌 Experiencia llevando modelos a producción.\n"
            "📌 Sólida base estadística."
        ),
        "requisitos_deseables": (
            "⭐ Experiencia con frameworks de deep learning (PyTorch/TensorFlow).\n"
            "⭐ Conocimientos de MLOps.\n"
            "⭐ Publicaciones o proyectos propios de portafolio."
        ),
    },
    {
        "titulo": "Analista de Reclutamiento y Selección — Semi-Senior",
        "categoria": "Recursos Humanos",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "🧑‍💼 Buscamos un/a Analista de Reclutamiento y Selección para gestionar procesos "
            "de principio a fin, desde la publicación de vacantes hasta el seguimiento del "
            "onboarding de los nuevos ingresos."
        ),
        "funciones": (
            "📢 Publicar y difundir vacantes en distintos canales.\n"
            "🗂️ Filtrar hojas de vida y coordinar entrevistas.\n"
            "🎤 Realizar entrevistas por competencias.\n"
            "🤝 Dar seguimiento al proceso de onboarding de nuevos colaboradores."
        ),
        "requisitos": (
            "📌 2-3 años de experiencia en reclutamiento y selección.\n"
            "📌 Manejo de entrevistas por competencias.\n"
            "📌 Manejo de algún ATS (Bitrix24, Lever u otro) y LinkedIn Recruiter.\n"
            "📌 Estudios en Psicología, Administración o carreras afines."
        ),
        "requisitos_deseables": (
            "⭐ Experiencia reclutando perfiles tecnológicos.\n"
            "⭐ Conocimientos de assessment center y pruebas psicométricas online."
        ),
    },
    {
        "titulo": "Ejecutivo/a de Ventas B2B — Sin Experiencia",
        "categoria": "Ventas",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 3,
        "descripcion": (
            "💼 ¿Buscas iniciar tu carrera en ventas? Empresa en crecimiento busca "
            "Ejecutivos/as de Ventas B2B con actitud comercial y ganas de aprender. Se "
            "brinda capacitación completa desde el primer día."
        ),
        "funciones": (
            "📞 Prospectar y contactar clientes potenciales.\n"
            "🤝 Presentar la propuesta de valor a empresas.\n"
            "📈 Realizar seguimiento a la cartera de clientes asignada.\n"
            "🎯 Cumplir metas comerciales mensuales."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa — se capacita en el puesto.\n"
            "📌 Estudios técnicos o universitarios en curso o culminados.\n"
            "📌 Facilidad de comunicación y orientación a resultados.\n"
            "📌 Disponibilidad a tiempo completo."
        ),
        "requisitos_deseables": (
            "⭐ Experiencia previa en atención al cliente o call center.\n"
            "⭐ Manejo de CRM (Salesforce, HubSpot o Zoho)."
        ),
    },
    {
        "titulo": "Key Account Manager — Senior",
        "categoria": "Ventas",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 1,
        "descripcion": (
            "🏆 Buscamos un/a Key Account Manager Senior para gestionar la relación con "
            "las cuentas más importantes de la empresa, identificando oportunidades de "
            "crecimiento y asegurando altos niveles de satisfacción."
        ),
        "funciones": (
            "🤝 Gestionar y fidelizar la cartera de cuentas clave.\n"
            "📊 Elaborar planes comerciales por cuenta.\n"
            "💰 Negociar renovaciones y ampliaciones de contrato.\n"
            "🔄 Coordinar con áreas internas para asegurar el servicio."
        ),
        "requisitos": (
            "📌 5+ años de experiencia gestionando cuentas corporativas.\n"
            "📌 Manejo de CRM (Salesforce o HubSpot) para gestión de pipeline y cuentas.\n"
            "📌 Habilidades de negociación comercial comprobadas.\n"
            "📌 Estudios en Administración, Marketing o afines."
        ),
        "requisitos_deseables": (
            "⭐ Experiencia en el sector B2B o corporativo.\n"
            "⭐ Inglés intermedio-avanzado."
        ),
    },
    {
        "titulo": "Representante de Atención al Cliente — Sin Experiencia",
        "categoria": "Atención al Cliente",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 4,
        "descripcion": (
            "😊 Sumamos talento a nuestro equipo de Atención al Cliente. Buscamos personas "
            "con buena actitud de servicio, para brindar soporte y resolver consultas de "
            "los clientes de forma amable y efectiva."
        ),
        "funciones": (
            "☎️ Atender consultas y reclamos de clientes por distintos canales.\n"
            "📝 Registrar cada caso en el sistema interno.\n"
            "🔄 Derivar casos complejos al área correspondiente.\n"
            "⭐ Cuidar la satisfacción del cliente en cada interacción."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa.\n"
            "📌 Secundaria completa, estudios técnicos en curso son un plus.\n"
            "📌 Buena dicción y trato amable.\n"
            "📌 Disponibilidad para trabajar en turnos rotativos."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa en atención al público.\n⭐ Manejo de sistemas de tickets (Zendesk, Freshdesk u otro)."),
    },
    {
        "titulo": "Asistente Administrativo/a — Practicante",
        "categoria": "Administración / Oficina",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "🗂️ Buscamos un/a practicante de Administración para apoyar en tareas de "
            "oficina y gestión documentaria, en un ambiente donde podrá aprender de "
            "principio a fin la operación administrativa de la empresa."
        ),
        "funciones": (
            "📁 Organizar y archivar documentación física y digital.\n"
            "📅 Coordinar agendas y reuniones.\n"
            "🧾 Apoyar en la gestión de proveedores y compras menores.\n"
            "📊 Elaborar reportes simples en Excel."
        ),
        "requisitos": (
            "📌 Estudiante técnico/universitario de Administración o carreras afines.\n"
            "📌 Manejo básico de Office (Word, Excel).\n"
            "📌 Organización y proactividad.\n"
            "📌 Disponibilidad para prácticas."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa como practicante en otra área administrativa."),
    },
    {
        "titulo": "Analista Contable — Semi-Senior",
        "categoria": "Contabilidad / Finanzas",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "📈 Buscamos un/a Analista Contable Semi-Senior para sumarse al equipo de "
            "Finanzas, encargándose del registro contable, conciliaciones y apoyo en el "
            "cierre mensual."
        ),
        "funciones": (
            "🧮 Registrar operaciones contables en el sistema.\n"
            "🔄 Realizar conciliaciones bancarias.\n"
            "📅 Apoyar en el cierre contable mensual.\n"
            "📄 Preparar reportes para la gerencia de Finanzas."
        ),
        "requisitos": (
            "📌 2-4 años de experiencia en el área contable.\n"
            "📌 Egresado/a o titulado/a en Contabilidad.\n"
            "📌 Manejo de algún ERP contable (SAP, Concar u otro).\n"
            "📌 Conocimientos tributarios básicos."
        ),
        "requisitos_deseables": ("⭐ Estudios de especialización en tributación o NIIF."),
    },
    {
        "titulo": "Especialista en Marketing Digital — Semi-Senior",
        "categoria": "Marketing",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 1,
        "descripcion": (
            "📣 Buscamos un/a Especialista en Marketing Digital para planificar y ejecutar "
            "campañas en redes sociales y buscadores, con foco en el crecimiento de la "
            "marca y la generación de leads."
        ),
        "funciones": (
            "📱 Planificar y ejecutar campañas en redes sociales.\n"
            "🔍 Gestionar campañas de pauta digital (Meta Ads, Google Ads).\n"
            "📊 Analizar métricas de desempeño y proponer mejoras.\n"
            "✍️ Coordinar la creación de contenido con el equipo de diseño."
        ),
        "requisitos": (
            "📌 2-3 años de experiencia en marketing digital.\n"
            "📌 Manejo de Meta Ads y Google Ads.\n"
            "📌 Conocimientos de analítica web (Google Analytics).\n"
            "📌 Estudios en Marketing, Comunicaciones o afines."
        ),
        "requisitos_deseables": ("⭐ Experiencia con herramientas de email marketing.\n⭐ Nociones de SEO."),
    },
    {
        "titulo": "Coordinador/a de Logística — Semi-Senior",
        "categoria": "Logística / Almacén",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "📦 Buscamos un/a Coordinador/a de Logística para supervisar la operación de "
            "almacén y distribución, asegurando el cumplimiento de los tiempos de entrega "
            "y el buen manejo del inventario."
        ),
        "funciones": (
            "🚚 Coordinar la distribución y entrega de pedidos.\n"
            "📋 Supervisar el control de inventario en almacén.\n"
            "👥 Liderar al equipo operativo de almacén.\n"
            "📉 Reportar indicadores logísticos a la gerencia."
        ),
        "requisitos": (
            "📌 2-3 años de experiencia en logística o almacén.\n"
            "📌 Manejo de sistemas de gestión de inventario (WMS, SAP WM o similar).\n"
            "📌 Capacidad de liderazgo de equipos.\n"
            "📌 Disponibilidad para trabajar en almacén."
        ),
        "requisitos_deseables": ("⭐ Conocimientos de indicadores logísticos (KPIs).\n⭐ Licencia de conducir."),
    },
    {
        "titulo": "Enfermero/a Ocupacional — Semi-Senior",
        "categoria": "Salud",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "🏥 Buscamos un/a Enfermero/a Ocupacional para velar por la salud y seguridad "
            "de los colaboradores dentro de las instalaciones, dando soporte en programas "
            "de prevención y atención primaria."
        ),
        "funciones": (
            "🩺 Brindar atención primaria ante emergencias en planta.\n"
            "📋 Ejecutar programas de vigilancia de la salud ocupacional.\n"
            "💉 Coordinar campañas de vacunación y chequeos preventivos.\n"
            "📁 Mantener actualizadas las historias clínicas ocupacionales."
        ),
        "requisitos": (
            "📌 2+ años de experiencia como enfermero/a ocupacional.\n"
            "📌 Colegiatura y habilitación vigente.\n"
            "📌 Manejo de software de historia clínica electrónica (HCE).\n"
            "📌 Conocimientos en seguridad y salud en el trabajo.\n"
            "📌 Disponibilidad para trabajar en planta."
        ),
        "requisitos_deseables": ("⭐ Diplomado en Salud Ocupacional.\n⭐ Certificación en primeros auxilios."),
    },
    {
        "titulo": "Docente de Inglés — Sin Experiencia",
        "categoria": "Educación",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 2,
        "descripcion": (
            "📚 Buscamos Docentes de Inglés con buen nivel del idioma para dictar clases a "
            "estudiantes de distintos niveles. Ideal para egresados/as recientes que quieran "
            "iniciarse en la docencia, se brinda capacitación pedagógica inicial."
        ),
        "funciones": (
            "🗣️ Dictar clases de inglés según el nivel asignado.\n"
            "📝 Preparar material didáctico y evaluaciones.\n"
            "📊 Hacer seguimiento al progreso de los estudiantes.\n"
            "💬 Fomentar la participación activa en clase."
        ),
        "requisitos": (
            "📌 No se requiere experiencia docente previa.\n"
            "📌 Nivel de inglés avanzado o certificación internacional (B2/C1).\n"
            "📌 Estudios en Educación, Traducción o afines (o en curso).\n"
            "📌 Buena capacidad de comunicación."
        ),
        "requisitos_deseables": ("⭐ Certificación TEFL/TESOL.\n⭐ Experiencia dictando clases particulares."),
    },
    {
        "titulo": "Teleoperador/a — Sin Experiencia",
        "categoria": "Call Center",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 5,
        "descripcion": (
            "📞 ¡Únete a nuestro equipo de Call Center! Buscamos Teleoperadores/as para "
            "atención y venta telefónica, con buena actitud y ganas de aprender. "
            "Capacitación paga desde el primer día."
        ),
        "funciones": (
            "📲 Realizar llamadas salientes según campaña asignada.\n"
            "📋 Registrar cada gestión en el sistema.\n"
            "🎯 Cumplir metas diarias de gestión.\n"
            "🙋 Resolver dudas básicas de los clientes."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa.\n"
            "📌 Secundaria completa.\n"
            "📌 Buena dicción y facilidad de palabra.\n"
            "📌 Disponibilidad de horario full time o part time."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa en ventas o atención al cliente.\n⭐ Manejo de discadores/CRM de call center (Aloware, Genesys u otro)."),
    },
    {
        "titulo": "Diseñador/a Gráfico — Semi-Senior",
        "categoria": "Marketing",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 1,
        "descripcion": (
            "🎨 Buscamos un/a Diseñador/a Gráfico con ojo creativo y dominio de las "
            "herramientas de diseño, para producir piezas gráficas para redes sociales, "
            "campañas digitales y material corporativo."
        ),
        "funciones": (
            "🖌️ Diseñar piezas para redes sociales, email marketing y campañas digitales.\n"
            "📐 Adaptar el manual de marca a distintos formatos y soportes.\n"
            "🎬 Editar videos cortos para reels/historias.\n"
            "🤝 Coordinar con el equipo de Marketing los tiempos de entrega."
        ),
        "requisitos": (
            "📌 2-3 años de experiencia en diseño gráfico digital.\n"
            "📌 Dominio de Adobe Photoshop e Illustrator.\n"
            "📌 Manejo de Figma para piezas colaborativas.\n"
            "📌 Portafolio de trabajos previos."
        ),
        "requisitos_deseables": ("⭐ Nociones de edición de video (Premiere/CapCut).\n⭐ Motion graphics básico (After Effects)."),
    },
    {
        "titulo": "Diseñador/a UX/UI — Junior",
        "categoria": "Tecnología / Sistemas",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 1,
        "descripcion": (
            "🖥️ Buscamos un/a Diseñador/a UX/UI Junior para colaborar en el diseño de "
            "interfaces de nuestros productos digitales, trabajando codo a codo con el "
            "equipo de desarrollo."
        ),
        "funciones": (
            "🧩 Diseñar wireframes y prototipos de interfaz en Figma.\n"
            "🔍 Apoyar en investigación de usuarios y pruebas de usabilidad.\n"
            "🎨 Mantener consistencia con el sistema de diseño existente.\n"
            "🤝 Colaborar de cerca con desarrolladores frontend."
        ),
        "requisitos": (
            "📌 0-1 año de experiencia o proyectos de portafolio en UX/UI.\n"
            "📌 Manejo de Figma.\n"
            "📌 Nociones de principios de usabilidad y accesibilidad.\n"
            "📌 Estudios en Diseño, Sistemas o afines."
        ),
        "requisitos_deseables": ("⭐ Nociones básicas de HTML/CSS.\n⭐ Inglés básico para documentación."),
    },
    {
        "titulo": "Médico/a Ocupacional — Semi-Senior",
        "categoria": "Salud",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "🩺 Buscamos un/a Médico/a Ocupacional para liderar el programa de salud "
            "ocupacional de la empresa, realizando evaluaciones médicas y gestionando la "
            "vigilancia de la salud de los colaboradores."
        ),
        "funciones": (
            "🏥 Realizar exámenes médicos ocupacionales (ingreso, periódico, retiro).\n"
            "📋 Elaborar y dar seguimiento al programa de vigilancia médica.\n"
            "📊 Registrar historias clínicas en el sistema electrónico interno.\n"
            "🤝 Coordinar con el área de Seguridad y Salud en el Trabajo."
        ),
        "requisitos": (
            "📌 3+ años de experiencia en medicina ocupacional.\n"
            "📌 Colegiatura médica y RNE vigentes.\n"
            "📌 Manejo de software de historia clínica electrónica.\n"
            "📌 Disponibilidad para trabajar en planta."
        ),
        "requisitos_deseables": ("⭐ Diplomado en Medicina Ocupacional.\n⭐ Experiencia en el sector industrial."),
    },
    {
        "titulo": "Médico/a General — Consulta Externa — Senior",
        "categoria": "Salud",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 2,
        "descripcion": (
            "⚕️ Clínica en crecimiento busca Médicos/as Generales para atención de "
            "consulta externa, brindando un servicio cálido y de calidad a los pacientes."
        ),
        "funciones": (
            "🩺 Atender consultas médicas generales de forma presencial.\n"
            "📝 Registrar historias clínicas en el sistema (HIS).\n"
            "💊 Emitir recetas y órdenes de exámenes auxiliares.\n"
            "🔄 Derivar casos a especialistas cuando corresponda."
        ),
        "requisitos": (
            "📌 4+ años de experiencia en consulta externa.\n"
            "📌 Colegiatura médica (CMP) y RNE vigentes.\n"
            "📌 Manejo de sistemas HIS de historia clínica electrónica.\n"
            "📌 Disponibilidad de horario rotativo."
        ),
        "requisitos_deseables": ("⭐ Segunda especialidad afín.\n⭐ Experiencia en clínicas privadas."),
    },
    {
        "titulo": "Técnico/a de Mantenimiento Industrial — Semi-Senior",
        "categoria": "Mantenimiento Técnico",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 2,
        "descripcion": (
            "🔧 Buscamos un/a Técnico/a de Mantenimiento Industrial para asegurar el buen "
            "funcionamiento de la maquinaria de planta, ejecutando mantenimiento "
            "preventivo y correctivo."
        ),
        "funciones": (
            "⚙️ Ejecutar mantenimiento preventivo según cronograma.\n"
            "🛠️ Diagnosticar y reparar fallas mecánicas/eléctricas.\n"
            "📋 Registrar órdenes de trabajo en el sistema de mantenimiento (CMMS).\n"
            "🦺 Cumplir los protocolos de seguridad en planta."
        ),
        "requisitos": (
            "📌 2-3 años de experiencia en mantenimiento industrial.\n"
            "📌 Formación técnica en Mecánica, Electricidad o afines.\n"
            "📌 Conocimientos básicos de sistemas eléctricos/neumáticos.\n"
            "📌 Disponibilidad para turnos rotativos."
        ),
        "requisitos_deseables": ("⭐ Conocimientos de sistemas SCADA/PLC.\n⭐ Certificación en trabajos de alto riesgo."),
    },
    {
        "titulo": "Supervisor/a de Producción — Senior",
        "categoria": "Producción / Operaciones",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "🏭 Buscamos un/a Supervisor/a de Producción Senior para liderar el equipo de "
            "planta, asegurando el cumplimiento de metas de producción con los estándares "
            "de calidad y seguridad requeridos."
        ),
        "funciones": (
            "👥 Supervisar y coordinar al personal operativo de planta.\n"
            "📊 Controlar indicadores de producción (OEE, mermas) en Excel/ERP.\n"
            "🔄 Implementar mejoras bajo metodología Lean Manufacturing.\n"
            "🦺 Velar por el cumplimiento de normas de seguridad."
        ),
        "requisitos": (
            "📌 4+ años de experiencia supervisando líneas de producción.\n"
            "📌 Manejo avanzado de Excel para control de indicadores.\n"
            "📌 Conocimientos de Lean Manufacturing / mejora continua.\n"
            "📌 Estudios en Ingeniería Industrial o afines."
        ),
        "requisitos_deseables": ("⭐ Manejo de un ERP de producción (SAP PP u otro).\n⭐ Certificación Six Sigma."),
    },
    {
        "titulo": "Operario/a de Producción — Sin Experiencia",
        "categoria": "Producción / Operaciones",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 6,
        "descripcion": (
            "🏭 Empresa manufacturera busca Operarios/as de Producción para sumarse a la "
            "línea de planta, con oportunidad de línea de carrera dentro de la empresa."
        ),
        "funciones": (
            "⚙️ Operar máquinas de línea de producción según instructivo.\n"
            "✅ Realizar control de calidad básico del producto.\n"
            "📦 Apoyar en el embalaje y almacenamiento de producto terminado.\n"
            "🦺 Cumplir con los protocolos de seguridad de planta."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa.\n"
            "📌 Secundaria completa.\n"
            "📌 Disponibilidad para turnos rotativos.\n"
            "📌 Buen estado de salud física."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa en planta o manufactura."),
    },
    {
        "titulo": "Agente de Seguridad — Sin Experiencia",
        "categoria": "Servicios Generales / Limpieza / Seguridad",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 3,
        "descripcion": (
            "🛡️ Buscamos Agentes de Seguridad para resguardar nuestras instalaciones, "
            "brindando un servicio de vigilancia responsable y atento."
        ),
        "funciones": (
            "🚶 Realizar rondas de vigilancia dentro de las instalaciones.\n"
            "📋 Controlar el ingreso y salida de personal y visitas.\n"
            "📹 Monitorear cámaras de seguridad.\n"
            "📝 Reportar incidencias al supervisor de turno."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa (se valora experiencia militar/policial).\n"
            "📌 Secundaria completa.\n"
            "📌 Carné de vigilancia vigente o en trámite.\n"
            "📌 Disponibilidad para turnos rotativos."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa en seguridad privada."),
    },
    {
        "titulo": "Personal de Limpieza — Sin Experiencia",
        "categoria": "Servicios Generales / Limpieza / Seguridad",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 4,
        "descripcion": (
            "🧹 Buscamos Personal de Limpieza para mantener nuestras instalaciones en "
            "óptimas condiciones de higiene y orden."
        ),
        "funciones": (
            "🧽 Realizar limpieza de oficinas y áreas comunes.\n"
            "🗑️ Gestionar el manejo de residuos según protocolo interno.\n"
            "🧴 Controlar el stock de insumos de limpieza.\n"
            "✅ Reportar necesidades de mantenimiento al área correspondiente."
        ),
        "requisitos": (
            "📌 No se requiere experiencia previa.\n"
            "📌 Primaria o secundaria completa.\n"
            "📌 Responsabilidad y puntualidad.\n"
            "📌 Disponibilidad de horario."
        ),
        "requisitos_deseables": ("⭐ Experiencia previa en limpieza institucional."),
    },
    {
        "titulo": "Abogado/a Corporativo — Senior",
        "categoria": "Legal",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 1,
        "descripcion": (
            "⚖️ Buscamos un/a Abogado/a Corporativo Senior para asesorar legalmente a la "
            "empresa en materia societaria, contractual y regulatoria."
        ),
        "funciones": (
            "📄 Redactar y revisar contratos comerciales.\n"
            "🏢 Asesorar en temas societarios y de gobierno corporativo.\n"
            "🔍 Dar seguimiento a procesos regulatorios y de cumplimiento.\n"
            "🤝 Coordinar con estudios externos cuando sea necesario."
        ),
        "requisitos": (
            "📌 5+ años de experiencia en derecho corporativo.\n"
            "📌 Colegiatura vigente.\n"
            "📌 Manejo de SPIJ y plataformas de consulta legal.\n"
            "📌 Sólida redacción de contratos."
        ),
        "requisitos_deseables": ("⭐ Maestría en Derecho Corporativo o afines.\n⭐ Inglés avanzado."),
    },
    {
        "titulo": "Asistente Legal — Practicante",
        "categoria": "Legal",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "📚 Buscamos un/a practicante de Derecho para apoyar al área Legal en la "
            "elaboración de documentos y el seguimiento de trámites administrativos."
        ),
        "funciones": (
            "📄 Apoyar en la redacción de documentos legales simples.\n"
            "🔍 Realizar búsquedas y seguimiento de expedientes.\n"
            "🗂️ Organizar el archivo documentario del área.\n"
            "📅 Dar seguimiento a plazos y vencimientos."
        ),
        "requisitos": (
            "📌 Estudiante de los últimos ciclos de Derecho.\n"
            "📌 Manejo de Word y Excel a nivel intermedio.\n"
            "📌 Organización y atención al detalle.\n"
            "📌 Disponibilidad para prácticas."
        ),
        "requisitos_deseables": ("⭐ Conocimientos de SPIJ.\n⭐ Cursos de redacción legal."),
    },
    {
        "titulo": "Consultor/a de Procesos — Semi-Senior",
        "categoria": "Consultoría",
        "modalidad": Puesto.Modalidad.HIBRIDO,
        "vacantes": 1,
        "descripcion": (
            "📈 Buscamos un/a Consultor/a de Procesos para acompañar a clientes en "
            "proyectos de mejora continua y optimización de procesos de negocio."
        ),
        "funciones": (
            "🔍 Levantar y documentar procesos actuales del cliente.\n"
            "📊 Analizar datos y proponer mejoras con indicadores claros.\n"
            "📑 Elaborar informes y presentaciones ejecutivas.\n"
            "🤝 Acompañar la implementación de las recomendaciones."
        ),
        "requisitos": (
            "📌 2-4 años de experiencia en consultoría o mejora de procesos.\n"
            "📌 Manejo avanzado de Excel y PowerPoint.\n"
            "📌 Conocimientos de metodologías ágiles o Lean.\n"
            "📌 Estudios en Ingeniería Industrial, Administración o afines."
        ),
        "requisitos_deseables": ("⭐ Manejo de Power BI.\n⭐ Certificación en Scrum o Lean Six Sigma."),
    },
    {
        "titulo": "Community Manager — Junior",
        "categoria": "Marketing",
        "modalidad": Puesto.Modalidad.REMOTO,
        "vacantes": 1,
        "descripcion": (
            "📱 Buscamos un/a Community Manager Junior, creativo/a y al día con las "
            "tendencias digitales, para gestionar nuestras redes sociales del día a día."
        ),
        "funciones": (
            "📅 Planificar y publicar contenido en el calendario editorial.\n"
            "💬 Responder mensajes y comentarios de la comunidad.\n"
            "📊 Reportar métricas básicas de alcance y engagement.\n"
            "🎬 Grabar y editar contenido corto para redes."
        ),
        "requisitos": (
            "📌 0-1 año de experiencia en manejo de redes sociales.\n"
            "📌 Manejo de Canva y Meta Business Suite.\n"
            "📌 Nociones de edición de video (CapCut o similar).\n"
            "📌 Buena redacción y creatividad."
        ),
        "requisitos_deseables": ("⭐ Experiencia manejando cuentas de marca (no personales).\n⭐ Nociones de fotografía de producto."),
    },
    {
        "titulo": "Contador/a Senior",
        "categoria": "Contabilidad / Finanzas",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 1,
        "descripcion": (
            "📊 Buscamos un/a Contador/a Senior para liderar el cierre contable y "
            "tributario mensual, asegurando el cumplimiento de las obligaciones formales "
            "de la empresa."
        ),
        "funciones": (
            "📅 Liderar el cierre contable mensual y anual.\n"
            "🧾 Elaborar y revisar declaraciones tributarias (PDT/PLE SUNAT).\n"
            "📊 Preparar estados financieros para gerencia.\n"
            "👥 Supervisar al equipo de analistas contables."
        ),
        "requisitos": (
            "📌 5+ años de experiencia en contabilidad general.\n"
            "📌 Colegiatura vigente (CPC).\n"
            "📌 Manejo de SAP o Concar y PLE SUNAT.\n"
            "📌 Sólidos conocimientos tributarios y de NIIF."
        ),
        "requisitos_deseables": ("⭐ Experiencia liderando auditorías externas.\n⭐ Inglés intermedio."),
    },
    {
        "titulo": "Especialista en Soporte TI (Help Desk) — Junior",
        "categoria": "Tecnología / Sistemas",
        "modalidad": Puesto.Modalidad.PRESENCIAL,
        "vacantes": 2,
        "descripcion": (
            "🖥️ Buscamos un/a Especialista en Soporte TI para brindar atención de primer "
            "nivel a los colaboradores, resolviendo incidencias de hardware, software y "
            "accesos."
        ),
        "funciones": (
            "🎫 Atender tickets de soporte (Zendesk/Freshdesk o similar).\n"
            "💻 Dar mantenimiento a equipos y resolver incidencias de software.\n"
            "🔐 Gestionar accesos y cuentas en Active Directory.\n"
            "📋 Documentar soluciones para la base de conocimiento."
        ),
        "requisitos": (
            "📌 1-2 años de experiencia en soporte técnico/help desk.\n"
            "📌 Conocimientos de Windows Server y Active Directory.\n"
            "📌 Manejo de herramientas de ticketing.\n"
            "📌 Estudios técnicos o universitarios en Sistemas o afines."
        ),
        "requisitos_deseables": ("⭐ Conocimientos básicos de redes.\n⭐ Certificación ITIL Foundation."),
    },
]


class Command(BaseCommand):
    help = "Siembra puestos de ejemplo (demo) para mostrar el catálogo público con contenido real."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reclutador",
            default="reclutador@example.com",
            help="Username o email del usuario Reclutador que figurará como creador de los puestos.",
        )

    def handle(self, *args, **options):
        identifier = options["reclutador"]
        User = get_user_model()
        try:
            reclutador = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist as exc:
            raise CommandError(
                f"No se encontró ningún usuario con username o email '{identifier}'."
            ) from exc

        creados = 0
        for data in PUESTOS:
            categoria = Categoria.objects.get(nombre=data["categoria"])
            _, created = Puesto.objects.get_or_create(
                titulo=data["titulo"],
                defaults={
                    "descripcion": data["descripcion"],
                    "funciones": data["funciones"],
                    "requisitos": data["requisitos"],
                    "requisitos_deseables": data["requisitos_deseables"],
                    "modalidad": data["modalidad"],
                    "vacantes": data["vacantes"],
                    "categoria": categoria,
                    "creado_por": reclutador,
                },
            )
            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"Creado: {data['titulo']}"))
            else:
                self.stdout.write(f"Ya existía, no se toca: {data['titulo']}")

        self.stdout.write(self.style.SUCCESS(f"Listo — {creados} puesto(s) nuevo(s) de {len(PUESTOS)} totales."))
