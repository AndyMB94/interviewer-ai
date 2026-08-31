import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.recruiting.management.commands.seed_puestos import _limite_postulaciones
from apps.recruiting.models import Puesto


@pytest.mark.parametrize(
    "titulo, esperado",
    [
        ("Teleoperador/a — Sin Experiencia", 100),
        ("DevOps / SRE Engineer — Senior", 15),
        ("Contador/a Senior", 15),
        ("Analista Contable — Semi-Senior", 50),
        ("Desarrollador/a Frontend React — Junior", 50),
    ],
)
def test_limite_postulaciones_se_deriva_del_titulo(titulo, esperado):
    assert _limite_postulaciones(titulo) == esperado


@pytest.mark.django_db
def test_seed_puestos_marca_los_dos_puestos_indicados_como_cerrados():
    reclutador = get_user_model().objects.create_user(
        "reclutador_seed", email="reclutador_seed@example.com", password="testpass123"
    )

    call_command("seed_puestos", "--reclutador=reclutador_seed@example.com")

    cerrados = set(
        Puesto.objects.filter(estado=Puesto.Estado.CERRADO).values_list("titulo", flat=True)
    )
    assert cerrados == {"Asistente Administrativo/a — Practicante", "Community Manager — Junior"}

    abiertos_de_muestra = Puesto.objects.get(titulo="Desarrollador/a Frontend React — Junior")
    assert abiertos_de_muestra.estado == Puesto.Estado.ABIERTO
    assert abiertos_de_muestra.limite_postulaciones == 50

    masivo = Puesto.objects.get(titulo="Teleoperador/a — Sin Experiencia")
    assert masivo.limite_postulaciones == 100

    senior = Puesto.objects.get(titulo="Data Scientist — Senior")
    assert senior.limite_postulaciones == 15
