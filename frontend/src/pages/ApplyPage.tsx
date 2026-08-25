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
import { fetchCategorias, fetchPuestosAbiertos, type Categoria, type Puesto } from "@/lib/api";

export function ApplyPage() {
  const [puestos, setPuestos] = useState<Puesto[]>([]);
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
    fetchPuestosAbiertos(categoriaId === "todas" ? undefined : Number(categoriaId))
      .then(setPuestos)
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoadingPuestos(false));
  }, [categoriaId]);

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-4 pt-8 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">Vacantes abiertas</h1>
        <p className="text-muted-foreground">
          Elija un puesto y postule subiendo su CV — sin necesidad de crear una cuenta.
        </p>
      </header>

      <div className="flex justify-center">
        <Select value={categoriaId} onValueChange={(value) => setCategoriaId(value ?? "todas")}>
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

      <div className="grid gap-4 sm:grid-cols-2">
        {loadingPuestos
          ? Array.from({ length: 4 }).map((_, index) => <PuestoCardSkeleton key={index} />)
          : puestos.map((puesto, index) => (
              <div
                key={puesto.id}
                className="animate-in fade-in-0 slide-in-from-bottom-2 fill-mode-both duration-300"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <PuestoCard puesto={puesto} />
              </div>
            ))}
      </div>
    </div>
  );
}
