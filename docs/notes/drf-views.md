# DRF: tipos de vistas

Apunte de repaso — no es documentación del proyecto, es referencia personal para tener en cuenta mientras se avanza con Django/DRF. Se actualiza a medida que se entiende mejor cada cosa o aparecen casos nuevos en el proyecto real.

## Function-Based Views (FBV) vs Class-Based Views (CBV)

Antes de la pregunta de "cuál usar", está la distinción de fondo: de las 4 opciones, solo `@api_view` es una **función**. `APIView`, `generics.*` y `ViewSet` son todas **clases**, y además forman una jerarquía de herencia entre sí:

```
View (Django, la base de todo)
 └── APIView (DRF: agrega request/response de DRF, negociación de contenido, etc.)
       ├── GenericAPIView → ListAPIView, CreateAPIView, ListCreateAPIView... (generics)
       └── ViewSet → GenericViewSet → ModelViewSet
```

`generics.ListCreateAPIView` hereda de `APIView` (con capas intermedias) y le suma comportamiento de "ya sé hacer list/create sobre un queryset". `ModelViewSet` agrupa las 5 operaciones CRUD en una sola clase, pensada para que un `Router` la conecte a las urls.

| | FBV (`@api_view`) | CBV (`APIView` y todo lo que hereda de ella) |
|---|---|---|
| Cómo se comparte código | Copiar/pegar o armar funciones auxiliares propias | Por **herencia**: heredás de una clase que ya viene con métodos hechos |
| Qué tan explícito es | Todo lo que hace la vista está a la vista, en un solo lugar | Parte del comportamiento vive en la clase padre (no se ve directamente en el archivo, hay que saber qué hereda) |
| Dónde conviene | Lógica puntual, poca o ninguna repetición con otras vistas | Cuando el patrón se repite mucho (CRUD estándar) y no se quiere reescribir list/create/update/delete cada vez |

Trade-off de fondo: **FBV hace escribir más, pero se ve todo**. **CBV hace escribir menos, a cambio de más indirección** (parte del comportamiento queda "escondido" en la clase de la que se hereda) — el clásico costo/beneficio de la herencia.

## La pregunta base

Antes de elegir un tipo de vista, dos preguntas:

1. **¿Es una acción puntual (un verbo) o un recurso (un sustantivo con datos guardados)?**
   Ej: "preguntame algo" (verbo, acción) vs. "las entrevistas" (sustantivo, recurso con CRUD).
2. Si es un recurso: **¿necesito las 5 operaciones CRUD completas, tal cual, sin reglas especiales?**

## Tabla de decisión

| Caso | Opción |
|---|---|
| Acción puntual, sin modelo detrás (`/health/`, `/ask/`) | `@api_view` |
| Un endpoint con lógica distinta por método HTTP, sin ser CRUD | `APIView` |
| CRUD parcial sobre un modelo (ej. solo listar + crear, nunca borrar) | `generics.*` |
| CRUD completo y estándar sobre un modelo | `ModelViewSet` + `Router` |

---

## 1. Función + `@api_view`

```python
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
```

Es una función normal de Python. El **decorador** es lo que la conecta con DRF.

**¿Por qué decorador y no clase?** Porque una función no tiene una forma natural de "declarar" qué métodos HTTP acepta ni de exponer los atributos que DRF necesita (permisos, parsers, etc.) — no se puede heredar de algo si la vista es solo una función. El decorador envuelve la función por afuera y le inyecta ese comportamiento (valida el método HTTP, le da a `request` las capacidades de DRF, permite devolver un `Response` en vez de armar `JsonResponse` a mano).

Uso típico: endpoints puntuales que no calzan en un CRUD. Ejemplo real del proyecto: `/api/health/`, futuro `/api/ask/` (Fase 1, todavía sin persistencia — recibe texto, devuelve la respuesta del LLM, no hay "recurso" que listar).

```python
@api_view(["POST"])
def ask(request):
    question = request.data["question"]
    answer = llm_service.ask(question)
    return Response({"answer": answer})
```

---

## 2. Clase + `APIView`

```python
class InterviewSessionView(APIView):
    def get(self, request):
        session = InterviewSession.get_active(request.user)
        return Response({"state": session.state})

    def post(self, request):
        session = InterviewSession.get_active(request.user)
        session.force_end()
        return Response({"state": session.state})
```

Cada método HTTP es un método de la clase (`get`, `post`, `put`, `delete`...). Es el equivalente en clase de `@api_view` — útil cuando un mismo endpoint necesita comportamiento distinto por método HTTP y ese comportamiento no tiene nada que ver entre sí (acá `GET` consulta estado, `POST` fuerza el cierre de la sesión — dos acciones separadas, no "leer vs escribir el mismo recurso" al estilo CRUD).

Si se usara una sola función con `@api_view(["GET", "POST"])` y un `if request.method == ...` adentro, se mezclarían dos lógicas separadas en un solo bloque — la clase separa cada una en su propio método.

---

## 3. Vistas genéricas (`generics.*`)

```python
class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
```

Ya asumen que se está haciendo CRUD sobre un modelo, pero **solo el subconjunto de operaciones que se declara**. `ListCreateAPIView` da `GET` (listar) y `POST` (crear) — no existe ni siquiera la ruta para `DELETE`.

Útil cuando un recurso no debe soportar todas las operaciones. Ejemplo: si `Question` nunca se debe poder borrar ni editar una vez creada (registro histórico de la entrevista), `ListCreateAPIView` nunca genera esa capacidad — más seguro que usar un `ModelViewSet` completo y después tener que bloquear a mano los métodos que no se querían dar.

Otras vistas genéricas comunes: `RetrieveAPIView` (solo detalle), `RetrieveUpdateDestroyAPIView` (detalle + editar + borrar, sin listar/crear), `ListAPIView` (solo listar).

---

## 4. `ViewSet` + `Router`

```python
# serializers.py
class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ["id", "created_at", "status"]

# views.py
class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer

# urls.py
router = DefaultRouter()
router.register("interviews", InterviewViewSet)
urlpatterns = router.urls
```

Un `ViewSet` agrupa **todas** las operaciones de un recurso (list, retrieve, create, update, delete) en una sola clase. En vez de escribir las rutas a mano, un `Router` las genera automáticamente:

| Método + URL | Qué hace |
|---|---|
| `GET /api/interviews/` | lista todas |
| `POST /api/interviews/` | crea una |
| `GET /api/interviews/5/` | detalle de la #5 |
| `PUT /api/interviews/5/` | edita la #5 completa |
| `PATCH /api/interviews/5/` | edita parcialmente |
| `DELETE /api/interviews/5/` | borra la #5 |

Nadie escribe ese código a mano — el `ViewSet` ya sabe hacer las 5 cosas porque se le dio el modelo y el serializer. Tiene sentido cuando **es exactamente el CRUD de libro**, sin reglas especiales. Es la opción más "mágica" — hay que saber de memoria la convención de URLs/métodos para entender qué dispara qué, a cambio de escribir mucho menos código.

---

## Notas del proyecto (dónde aplica cada cosa acá)

- `/api/health/` (Backend Fase 0.3) → `@api_view`, ya implementado así.
- `/api/ask/` (Backend Fase 1.2) → candidato a `@api_view`, mismo motivo: acción puntual, sin modelo/persistencia todavía en esa fase.
- `Interview` / `Question` / `Answer` (Backend Fase 6, cuando exista persistencia) → a definir caso por caso con la tabla de arriba; probablemente `ModelViewSet` para `Interview` si se necesita CRUD completo, y algo más restringido (`generics.ListCreateAPIView` o similar) para `Question`/`Answer` si no deben editarse/borrarse una vez creadas.
