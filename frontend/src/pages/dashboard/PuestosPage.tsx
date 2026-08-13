import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/context/AuthContext";
import { fetchMisPuestos, type Puesto } from "@/lib/api";

export function PuestosPage() {
  const { accessToken } = useAuth();
  const [puestos, setPuestos] = useState<Puesto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPuestos(accessToken)
      .then(setPuestos)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [accessToken]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mis puestos</h1>

      {loading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full" />
          ))}
        </div>
      )}
      {error && <p className="text-destructive">{error}</p>}
      {!loading && !error && puestos.length === 0 && (
        <p className="text-muted-foreground">Todavía no publicaste ningún puesto.</p>
      )}

      {!loading && !error && puestos.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Título</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Postulaciones</TableHead>
              <TableHead>Vacantes</TableHead>
              <TableHead>Preseleccionados</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {puestos.map((puesto) => (
              <TableRow key={puesto.id}>
                <TableCell>{puesto.titulo}</TableCell>
                <TableCell>
                  <Badge variant={puesto.estado === "abierto" ? "default" : "secondary"}>
                    {puesto.estado}
                  </Badge>
                </TableCell>
                <TableCell>{puesto.postulaciones_count}</TableCell>
                <TableCell>{puesto.vacantes}</TableCell>
                <TableCell>{puesto.preseleccionados}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
