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
    acepta_postulaciones = serializers.BooleanField(read_only=True)

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
            "limite_postulaciones",
            "acepta_postulaciones",
            "creado_por",
            "created_at",
            "postulaciones_count",
            "preseleccionados",
        ]
        read_only_fields = ["creado_por", "created_at"]


MAX_CV_SIZE_MB = 5
MAX_CV_SIZE_BYTES = MAX_CV_SIZE_MB * 1024 * 1024


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
        # DRF genera solo un validador automático a partir del UniqueConstraint del modelo
        # (mensaje genérico en inglés, en non_field_errors) -- se desactiva para quedarse solo
        # con el de validate() de abajo, que da un mensaje claro en español sobre el campo email.
        validators = []

    def validate_puesto(self, puesto):
        # Cubre tanto un puesto cerrado a mano como uno que llegó a su límite de postulaciones
        # (Fase 10.13) -- mismo mensaje para los dos casos, sin distinguir el motivo (Decisión 9).
        if not puesto.acepta_postulaciones:
            raise serializers.ValidationError("Este puesto ya no acepta postulaciones.")
        return puesto

    def validate_cv(self, value):
        if value.size > MAX_CV_SIZE_BYTES:
            raise serializers.ValidationError(f"El CV no puede pesar más de {MAX_CV_SIZE_MB}MB.")
        return value

    def validate_email(self, value):
        # Normalizado para que la restricción de "un email, un puesto" (Infra Fase 6) no se
        # evada con mayúsculas/minúsculas distintas -- Andy@X y andy@X son el mismo email.
        return value.strip().lower()

    def validate(self, attrs):
        if Postulacion.objects.filter(puesto=attrs["puesto"], email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "Ya se registró una postulación con este email para este puesto."}
            )
        return attrs

    def get_interview_id(self, obj):
        interview = next(iter(obj.interviews.all()), None)
        return interview.id if interview else None
