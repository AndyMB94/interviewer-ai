import { useEffect, useState } from "react";
import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/context/AuthContext";
import { fetchMisPostulaciones, type Postulacion } from "@/lib/api";

const ESTADO_VARIANT: Record<Postulacion["estado"], "outline" | "default" | "destructive"> = {
  pendiente: "outline",
  aprobado: "default",
  rechazado: "destructive",
};

export function PostulacionesPage() {
  const { accessToken } = useAuth();
  const [postulaciones, setPostulaciones] = useState<Postulacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPostulaciones(accessToken)
      .then(setPostulaciones)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [accessToken]);

  return (
    <div className="space-y-4 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <h1 className="text-2xl font-bold">Postulaciones</h1>

      {loading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full" />
          ))}
        </div>
      )}
      {error && <p className="text-destructive">{error}</p>}
      {!loading && !error && postulaciones.length === 0 && (
        <p className="text-muted-foreground">Todavía no recibiste postulaciones.</p>
      )}

      {!loading && !error && postulaciones.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Puesto</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {postulaciones.map((postulacion) => (
              <TableRow key={postulacion.id}>
                <TableCell>{postulacion.nombre}</TableCell>
                <TableCell>{postulacion.email}</TableCell>
                <TableCell>{postulacion.puesto_titulo}</TableCell>
                <TableCell>
                  <Badge variant={ESTADO_VARIANT[postulacion.estado]}>{postulacion.estado}</Badge>
                </TableCell>
                <TableCell>
                  {postulacion.interview_id !== null && (
                    <Button
                      variant="outline"
                      size="sm"
                      nativeButton={false}
                      render={<Link to={`/dashboard/entrevistas/${postulacion.interview_id}`} />}
                    >
                      Ver entrevista
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
