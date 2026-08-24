from rest_framework import serializers

from apps.recruiting.models import Categoria, Postulacion, Puesto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class PuestoSerializer(serializers.ModelSerializer):
    postulaciones_count = serializers.IntegerField(read_only=True, default=0)
    preseleccionados = serializers.IntegerField(read_only=True, default=0)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, default=None)

    class Meta:
        model = Puesto
        fields = [
            "id",
            "titulo",
            "descripcion",
            "funciones",
            "requisitos",
            "requisitos_deseables",
            "modalidad",
            "vacantes",
            "categoria",
            "categoria_nombre",
            "estado",
            "creado_por",
            "created_at",
            "postulaciones_count",
            "preseleccionados",
        ]
        read_only_fields = ["creado_por", "created_at"]


class PostulacionSerializer(serializers.ModelSerializer):
    puesto_titulo = serializers.CharField(source="puesto.titulo", read_only=True)
    interview_id = serializers.SerializerMethodField()

    class Meta:
        model = Postulacion
        fields = [
            "id",
            "puesto",
            "puesto_titulo",
            "nombre",
            "email",
            "cv",
            "estado",
            "resultado_filtro",
            "created_at",
            "interview_id",
        ]
        read_only_fields = ["estado", "resultado_filtro", "created_at"]

    def validate_puesto(self, puesto):
        if puesto.estado != Puesto.Estado.ABIERTO:
            raise serializers.ValidationError("Este puesto ya no acepta postulaciones.")
        return puesto

    def get_interview_id(self, obj):
        interview = next(iter(obj.interviews.all()), None)
        return interview.id if interview else None
