from rest_framework import serializers

from apps.recruiting.models import Puesto


class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        fields = ["id", "titulo", "descripcion", "requisitos", "estado", "creado_por", "created_at"]
        read_only_fields = ["creado_por", "created_at"]
