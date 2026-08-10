import tempfile

import pytest


@pytest.fixture(autouse=True)
def _use_temp_media_root(settings):
    """Evita que los tests que suben archivos (ej. CVs) escriban en backend/media/ real."""
    settings.MEDIA_ROOT = tempfile.mkdtemp()
