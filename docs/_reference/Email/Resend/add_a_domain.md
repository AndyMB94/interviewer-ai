# Resend — Agregar y verificar un dominio

Fuente: https://resend.com/docs/add-a-domain

## Por qué un subdominio, no el dominio raíz

Resend recomienda usar un subdominio (ej. `mail.vacantia.dev` o `notificaciones.andymallcco.dev`) en vez del dominio raíz — aísla la reputación de envío de emails del resto del dominio (útil si el dominio raíz también sirve la web/API).

## Formas de agregarlo

Igual que los API keys, cuatro formas: Dashboard, REST API, CLI, o servidor MCP de Resend. Acá cubrimos el flujo del Dashboard.

## Pasos

1. Ir al [Domains Dashboard](https://resend.com/domains) → **Add Domain**.
2. Escribir el subdominio elegido. Cada subdominio se configura y verifica por separado (se pueden tener varios asociados a la misma raíz). Si el dominio ya está en uso por otra cuenta, el dashboard avisa y permite "reclamarlo" (`claim the domain`) para transferirlo — no debería pasar con un dominio propio nuevo.
3. Elegir la región más cercana a los destinatarios (Perú → revisar cuál está disponible más cerca al momento de configurarlo).
4. (Opcional) Personalizar el subdominio de Return-Path — si no se toca, usa `send.<tu-dominio>` por default.
5. Agregar los registros DNS que Resend genera (DKIM y SPF como **TXT**, más un **MX**) en el proveedor de DNS — **en este proyecto, Porkbun** (mismo panel donde ya se configuró el registro A para `interviewer.andymallcco.dev`, ver DECISIONS.md). Deben copiarse **exactos** (copiar/pegar, no tipear a mano) — la doc de Resend tiene guías por proveedor de DNS si hace falta.
6. Esperar verificación — normalmente ~15 minutos, hasta 72hs en casos raros. Se puede chequear con la herramienta `dns.email` de Resend si los registros ya son visibles públicamente; si pasan 72hs sin verificar, hay un botón "Restart verification" en el dashboard.
7. Una vez verificado, agregar el registro DMARC (lo da Resend después de la verificación inicial) — protege contra spoofing del dominio, importante para deliverability.
8. Opcional: activar tracking de aperturas/clicks, o forzar TLS.

## Nota importante

Los valores exactos de los registros (nombre/tipo/valor de cada TXT/MX) son específicos de cada cuenta/dominio — Resend los genera en el momento desde su dashboard (pestaña "Records" del dominio agregado), no están en la documentación pública. Hay que copiarlos de ahí al agregar el dominio real.
