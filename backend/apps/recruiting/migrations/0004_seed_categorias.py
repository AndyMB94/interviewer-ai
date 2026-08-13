from django.db import migrations

CATEGORIA_NAMES = [
    "Tecnología / Sistemas",
    "Análisis de Datos",
    "Recursos Humanos",
    "Ventas",
    "Atención al Cliente",
    "Administración / Oficina",
    "Contabilidad / Finanzas",
    "Marketing",
    "Logística / Almacén",
    "Producción / Operaciones",
    "Mantenimiento Técnico",
    "Servicios Generales / Limpieza / Seguridad",
    "Legal",
    "Consultoría",
    "Salud",
    "Educación",
    "Call Center",
]


def create_categorias(apps, schema_editor):
    Categoria = apps.get_model("recruiting", "Categoria")
    for nombre in CATEGORIA_NAMES:
        Categoria.objects.get_or_create(nombre=nombre)


def remove_categorias(apps, schema_editor):
    Categoria = apps.get_model("recruiting", "Categoria")
    Categoria.objects.filter(nombre__in=CATEGORIA_NAMES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("recruiting", "0003_categoria_puesto_categoria"),
    ]

    operations = [migrations.RunPython(create_categorias, remove_categorias)]
