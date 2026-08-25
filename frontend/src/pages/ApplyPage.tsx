import { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PuestoCard } from "@/components/PuestoCard";
import { PuestoCardSkeleton } from "@/components/PuestoCardSkeleton";
import { PaginationControls } from "@/components/PaginationControls";
import { fetchCategorias, fetchPuestosAbiertos, type Categoria, type Puesto } from "@/lib/api";

export function ApplyPage() {
  const [puestos, setPuestos] = useState<Puesto[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loadingPuestos, setLoadingPuestos] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriaId, setCategoriaId] = useState<string>("todas");

  useEffect(() => {
    fetchCategorias()
      .then(setCategorias)
      .catch(() => setCategorias([]));
  }, []);

  useEffect(() => {
    setLoadingPuestos(true);
    fetchPuestosAbiertos(categoriaId === "todas" ? undefined : Number(categoriaId), page)
      .then((data) => {
        setPuestos(data.results);
        setCount(data.count);
      })
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoadingPuestos(false));
  }, [categoriaId, page]);

  const handleCategoriaChange = (value: string | null) => {
    setCategoriaId(value ?? "todas");
    setPage(1);
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-4 pt-8 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <header className="relative space-y-2 overflow-hidden py-6 text-center">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute top-1/2 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/20 blur-3xl"
        />
        <h1 className="text-3xl font-bold">Encuentre su próxima oportunidad</h1>
        <p className="text-muted-foreground">
          Postule con su CV en minutos y reciba una respuesta rápida sobre su postulación.
        </p>
      </header>

      <div className="flex justify-center">
        <Select value={categoriaId} onValueChange={handleCategoriaChange}>
          <SelectTrigger className="w-72">
            <SelectValue placeholder="Todas las categorías">
              {(value: string) =>
                value === "todas"
                  ? "Todas las categorías"
                  : (categorias.find((categoria) => String(categoria.id) === value)?.nombre ??
                    "Todas las categorías")
              }
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="todas">Todas las categorías</SelectItem>
              {categorias.map((categoria) => (
                <SelectItem key={categoria.id} value={String(categoria.id)}>
                  {categoria.nombre}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      {loadError && <p className="text-center text-destructive">{loadError}</p>}

      {!loadingPuestos && !loadError && puestos.length === 0 && (
        <p className="text-center text-muted-foreground">
          No hay vacantes abiertas por el momento. Vuelva a intentarlo más adelante.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {loadingPuestos
          ? Array.from({ length: 6 }).map((_, index) => <PuestoCardSkeleton key={index} />)
          : puestos.map((puesto, index) => (
              <div
                key={puesto.id}
                className="h-full animate-in fade-in-0 slide-in-from-bottom-2 fill-mode-both duration-300"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <PuestoCard puesto={puesto} />
              </div>
            ))}
      </div>

      {!loadingPuestos && !loadError && (
        <PaginationControls count={count} page={page} onPageChange={setPage} />
      )}
    </div>
  );
}
