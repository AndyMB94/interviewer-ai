from rest_framework import serializers

from apps.recruiting.models import Postulacion, Puesto


class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        fields = ["id", "titulo", "descripcion", "requisitos", "estado", "creado_por", "created_at"]
        read_only_fields = ["creado_por", "created_at"]


class PostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postulacion
        fields = ["id", "puesto", "nombre", "email", "cv", "estado", "resultado_filtro", "created_at"]
        read_only_fields = ["estado", "resultado_filtro", "created_at"]
