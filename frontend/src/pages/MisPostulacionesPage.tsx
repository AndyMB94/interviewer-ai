import { useEffect, useState } from "react";
import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { fetchMisPostulacionesTodas, type MiPostulacionCompleta } from "@/lib/api";

const ESTADO_VARIANT: Record<MiPostulacionCompleta["estado"], "outline" | "default" | "destructive"> = {
  pendiente: "outline",
  aprobado: "default",
  rechazado: "destructive",
};

const ESTADO_LABEL: Record<MiPostulacionCompleta["estado"], string> = {
  pendiente: "En revisión",
  aprobado: "Aprobada",
  rechazado: "No fue seleccionado",
};

function diasRestantes(fechaLimite: string): number {
  const ms = new Date(fechaLimite).getTime() - Date.now();
  return Math.max(0, Math.ceil(ms / (1000 * 60 * 60 * 24)));
}

export function MisPostulacionesPage() {
  const { accessToken } = useAuth();
  const [postulaciones, setPostulaciones] = useState<MiPostulacionCompleta[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPostulacionesTodas(accessToken)
      .then(setPostulaciones)
      .catch((error: Error) => setLoadError(error.message));
  }, [accessToken]);

  if (loadError) {
    return <p className="mx-auto max-w-2xl p-4 text-center text-destructive">{loadError}</p>;
  }

  if (!postulaciones) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 p-4 pt-8">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4 pt-8 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <h1 className="text-2xl font-bold">Mis postulaciones</h1>

      {postulaciones.length === 0 && (
        <p className="text-sm text-muted-foreground">Todavía no tiene ninguna postulación registrada.</p>
      )}

      {postulaciones.map((postulacion) => {
        const puedeEntrevistar =
          postulacion.estado === "aprobado" &&
          !postulacion.tiene_entrevista &&
          !postulacion.entrevista_vencida;

        return (
          <Card key={postulacion.id}>
            <CardHeader className="flex flex-row items-start justify-between gap-2">
              <div className="min-w-0">
                <CardTitle className="wrap-break-word">{postulacion.puesto.titulo}</CardTitle>
                <CardDescription>
                  Postuló el {new Date(postulacion.created_at).toLocaleDateString("es-PE")}
                </CardDescription>
              </div>
              <Badge variant={ESTADO_VARIANT[postulacion.estado]}>
                {ESTADO_LABEL[postulacion.estado]}
              </Badge>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              {postulacion.estado === "aprobado" && postulacion.entrevista_finalizada && (
                <p className="text-sm text-muted-foreground">
                  Entrevista completada — el equipo de reclutamiento la está revisando.
                </p>
              )}
              {postulacion.estado === "aprobado" &&
                postulacion.tiene_entrevista &&
                !postulacion.entrevista_finalizada && (
                  <p className="text-sm text-muted-foreground">Tiene una entrevista en curso.</p>
                )}
              {postulacion.estado === "aprobado" &&
                !postulacion.tiene_entrevista &&
                postulacion.entrevista_vencida && (
                  <p className="text-sm text-destructive">
                    El plazo para hacer la entrevista venció. Contacte al equipo de reclutamiento.
                  </p>
                )}
              {puedeEntrevistar && (
                <>
                  {postulacion.fecha_limite_entrevista && (
                    <p className="text-sm text-muted-foreground">
                      Le quedan {diasRestantes(postulacion.fecha_limite_entrevista)} día(s) para hacer
                      su entrevista.
                    </p>
                  )}
                  <Button nativeButton={false} render={<Link to="/entrevista" />} className="self-start">
                    Hacer mi entrevista
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
