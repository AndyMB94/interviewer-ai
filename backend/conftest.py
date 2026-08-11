import tempfile

import pytest


@pytest.fixture(autouse=True)
def _use_temp_media_root(settings):
    """Evita que los tests que suben archivos (ej. CVs) escriban en backend/media/ real."""
    settings.MEDIA_ROOT = tempfile.mkdtemp()


@pytest.fixture(autouse=True)
def _use_locmem_email_backend(settings):
    """Evita que los tests manden emails reales por Resend — usa el backend en memoria de Django,
    accesible en cada test vía django.core.mail.outbox."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
