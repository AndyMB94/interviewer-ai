from rest_framework import serializers

from apps.recruiting.models import Postulacion, Puesto


class PuestoSerializer(serializers.ModelSerializer):
    postulaciones_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Puesto
        fields = [
            "id",
            "titulo",
            "descripcion",
            "requisitos",
            "estado",
            "creado_por",
            "created_at",
            "postulaciones_count",
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

    def get_interview_id(self, obj):
        interview = next(iter(obj.interviews.all()), None)
        return interview.id if interview else None
