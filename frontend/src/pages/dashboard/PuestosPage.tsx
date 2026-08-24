import { useEffect, useState } from "react";
import { Link } from "react-router";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAuth } from "@/context/AuthContext";
import { fetchMisPuestos, updatePuesto, type Puesto } from "@/lib/api";

export function PuestosPage() {
  const { accessToken } = useAuth();
  const [puestos, setPuestos] = useState<Puesto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [puestoParaCerrar, setPuestoParaCerrar] = useState<Puesto | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPuestos(accessToken)
      .then(setPuestos)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [accessToken]);

  const cambiarEstado = async (puesto: Puesto, estado: Puesto["estado"]) => {
    if (!accessToken) return;
    const actualizado = await updatePuesto(accessToken, puesto.id, { estado });
    setPuestos((actuales) => actuales.map((p) => (p.id === actualizado.id ? actualizado : p)));
  };

  const confirmarCierre = async () => {
    if (!puestoParaCerrar) return;
    await cambiarEstado(puestoParaCerrar, "cerrado");
    setPuestoParaCerrar(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Mis puestos</h1>
        <Button nativeButton={false} render={<Link to="/dashboard/puestos/nuevo" />}>
          Nuevo puesto
        </Button>
      </div>

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
              <TableHead>Acciones</TableHead>
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
                <TableCell className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    nativeButton={false}
                    render={<Link to={`/dashboard/puestos/${puesto.id}/editar`} />}
                  >
                    Editar
                  </Button>
                  {puesto.estado === "abierto" ? (
                    <Button variant="outline" size="sm" onClick={() => setPuestoParaCerrar(puesto)}>
                      Cerrar puesto
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => cambiarEstado(puesto, "abierto")}>
                      Reabrir puesto
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <AlertDialog
        open={puestoParaCerrar !== null}
        onOpenChange={(open) => {
          if (!open) setPuestoParaCerrar(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Cerrar este puesto?</AlertDialogTitle>
            <AlertDialogDescription>
              "{puestoParaCerrar?.titulo}" dejará de aparecer en la postulación pública y de aceptar
              CVs nuevos. Podés reabrirlo cuando quieras.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmarCierre}>Cerrar puesto</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
