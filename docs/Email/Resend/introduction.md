# Resend — Introducción y quickstart

Fuente: https://resend.com/docs/introduction

## Qué es

Resend es una API de email para desarrolladores. Soporta dos tipos de envío:

- **Transactional emails**: comunicación event-driven, personalizada (este es el caso de uso de Vacantia — mandar credenciales cuando se aprueba una postulación).
- **Marketing campaigns**: broadcasts masivos a una lista de contactos (no aplica a este proyecto).

## Requisitos previos

1. Un dominio propio, verificado en Resend (ver `add_a_domain.md`).
2. Un API key activo (ver `api_keys.md`).

## Quickstarts disponibles

Resend tiene guías para 13+ lenguajes/frameworks (Node.js, Next.js, Express, Python, Ruby on Rails, Go, Rust, Elixir, Java, .NET, PHP, Laravel, CLI). Para este proyecto usamos la guía de **Django** (ver `django_integration.md`), ya que el backend es Django + DRF.

## Otras secciones de la documentación

- **Emails Dashboard**: tracking de actividad de envíos.
- **Domains**: configuración de dominios para deliverability.
- **Webhooks**: notificaciones de eventos (entregado, rebotado, abierto, etc.) hacia la app — útil a futuro si se quiere saber si el email de credenciales realmente llegó.

Índice completo de la documentación: `https://resend.com/docs/llms.txt`.
