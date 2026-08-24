import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/context/AuthContext";
import {
  createPuesto,
  fetchCategorias,
  fetchPuesto,
  updatePuesto,
  type Categoria,
  type Puesto,
} from "@/lib/api";

const MODALIDAD_LABEL: Record<Puesto["modalidad"], string> = {
  presencial: "Presencial",
  remoto: "Remoto",
  hibrido: "Híbrido",
};

export function PuestoFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEditing = Boolean(id);
  const navigate = useNavigate();
  const { accessToken } = useAuth();

  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(isEditing);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [funciones, setFunciones] = useState("");
  const [requisitos, setRequisitos] = useState("");
  const [requisitosDeseables, setRequisitosDeseables] = useState("");
  const [modalidad, setModalidad] = useState<Puesto["modalidad"]>("presencial");
  const [vacantes, setVacantes] = useState(1);
  const [categoriaId, setCategoriaId] = useState<string>("ninguna");

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    fetchCategorias()
      .then(setCategorias)
      .catch(() => setCategorias([]));
  }, []);

  useEffect(() => {
    if (!id) return;
    fetchPuesto(Number(id))
      .then((puesto) => {
        setTitulo(puesto.titulo);
        setDescripcion(puesto.descripcion);
        setFunciones(puesto.funciones);
        setRequisitos(puesto.requisitos);
        setRequisitosDeseables(puesto.requisitos_deseables);
        setModalidad(puesto.modalidad);
        setVacantes(puesto.vacantes);
        setCategoriaId(puesto.categoria ? String(puesto.categoria) : "ninguna");
      })
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!accessToken) return;

    setSubmitting(true);
    setSubmitError(null);
    const payload = {
      titulo,
      descripcion,
      funciones,
      requisitos,
      requisitos_deseables: requisitosDeseables,
      modalidad,
      vacantes,
      categoria: categoriaId === "ninguna" ? null : Number(categoriaId),
    };
    try {
      if (isEditing) {
        await updatePuesto(accessToken, Number(id), payload);
      } else {
        await createPuesto(accessToken, payload);
      }
      navigate("/dashboard");
    } catch (error) {
      setSubmitError((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (loadError) {
    return <p className="text-center text-destructive">{loadError}</p>;
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>{isEditing ? "Editar puesto" : "Nuevo puesto"}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="titulo">Título</Label>
              <Input
                id="titulo"
                value={titulo}
                onChange={(event) => setTitulo(event.target.value)}
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="descripcion">Descripción del empleo</Label>
              <Textarea
                id="descripcion"
                value={descripcion}
                onChange={(event) => setDescripcion(event.target.value)}
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="funciones">Funciones</Label>
              <Textarea
                id="funciones"
                value={funciones}
                onChange={(event) => setFunciones(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="requisitos">Requisitos</Label>
              <Textarea
                id="requisitos"
                value={requisitos}
                onChange={(event) => setRequisitos(event.target.value)}
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="requisitos-deseables">Requisitos deseables</Label>
              <Textarea
                id="requisitos-deseables"
                value={requisitosDeseables}
                onChange={(event) => setRequisitosDeseables(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Modalidad</Label>
              <Select
                value={modalidad}
                onValueChange={(value) => setModalidad(value as Puesto["modalidad"])}
              >
                <SelectTrigger className="w-full">
                  <SelectValue>{() => MODALIDAD_LABEL[modalidad]}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {(Object.keys(MODALIDAD_LABEL) as Puesto["modalidad"][]).map((valor) => (
                      <SelectItem key={valor} value={valor}>
                        {MODALIDAD_LABEL[valor]}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Categoría</Label>
              <Select value={categoriaId} onValueChange={(value) => setCategoriaId(value ?? "ninguna")}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Sin categoría">
                    {(value: string) =>
                      value === "ninguna"
                        ? "Sin categoría"
                        : (categorias.find((categoria) => String(categoria.id) === value)?.nombre ??
                          "Sin categoría")
                    }
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="ninguna">Sin categoría</SelectItem>
                    {categorias.map((categoria) => (
                      <SelectItem key={categoria.id} value={String(categoria.id)}>
                        {categoria.nombre}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="vacantes">Vacantes</Label>
              <Input
                id="vacantes"
                type="number"
                min={1}
                value={vacantes}
                onChange={(event) => setVacantes(Number(event.target.value))}
                required
              />
            </div>

            {submitError && <p className="text-sm text-destructive">{submitError}</p>}

            <div className="flex gap-2">
              <Button type="submit" disabled={submitting}>
                {submitting && <Spinner data-icon="inline-start" />}
                {submitting ? "Guardando..." : "Guardar"}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/dashboard")}>
                Cancelar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
