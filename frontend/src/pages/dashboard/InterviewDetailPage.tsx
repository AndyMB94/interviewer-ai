import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import {
  fetchInterviewDetail,
  updateInterviewDecision,
  type InterviewDecision,
  type InterviewDetail,
} from "@/lib/api";

const ESTADO_VARIANT: Record<InterviewDetail["postulacion"]["estado"], "outline" | "default" | "destructive"> = {
  pendiente: "outline",
  aprobado: "default",
  rechazado: "destructive",
};

const DECISION_VARIANT: Record<InterviewDecision, "outline" | "default" | "destructive"> = {
  pendiente: "outline",
  avanza: "default",
  no_avanza: "destructive",
};

const DECISION_LABEL: Record<InterviewDecision, string> = {
  pendiente: "Pendiente",
  avanza: "Avanza a la siguiente etapa",
  no_avanza: "No avanza",
};

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("es-PE", { dateStyle: "medium", timeStyle: "short" });
}

export function InterviewDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { accessToken } = useAuth();
  const [interview, setInterview] = useState<InterviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingDecision, setUpdatingDecision] = useState(false);

  useEffect(() => {
    if (!accessToken || !id) return;
    fetchInterviewDetail(accessToken, Number(id))
      .then(setInterview)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [accessToken, id]);

  const handleDecision = async (decision: InterviewDecision) => {
    if (!accessToken || !id || !interview) return;
    const confirmar = window.confirm(
      decision === "avanza"
        ? "¿Confirma que este candidato avanza a la siguiente etapa?"
        : "¿Confirma que este candidato no avanza?",
    );
    if (!confirmar) return;

    setUpdatingDecision(true);
    try {
      await updateInterviewDecision(accessToken, Number(id), decision);
      setInterview({ ...interview, decision });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUpdatingDecision(false);
    }
  };

  return (
    <div className="space-y-4">
      <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/dashboard/postulaciones" />}>
        <ArrowLeft />
        Volver a postulaciones
      </Button>

      {loading && <p className="text-muted-foreground">Cargando...</p>}
      {error && <p className="text-destructive">{error}</p>}

      {!loading && !error && interview && (
        <>
          <div>
            <h1 className="text-2xl font-bold">{interview.postulacion.nombre}</h1>
            <p className="text-muted-foreground">{interview.postulacion.puesto_titulo}</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Resultado del filtro de CV
                <Badge variant={ESTADO_VARIANT[interview.postulacion.estado]}>
                  {interview.postulacion.estado}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-line text-sm">
                {interview.postulacion.resultado_filtro || "Sin resultado registrado."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Decisión
                <Badge variant={DECISION_VARIANT[interview.decision]}>
                  {DECISION_LABEL[interview.decision]}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex gap-2">
              <Button
                disabled={updatingDecision || interview.decision === "avanza"}
                onClick={() => handleDecision("avanza")}
              >
                Avanza a la siguiente etapa
              </Button>
              <Button
                variant="destructive"
                disabled={updatingDecision || interview.decision === "no_avanza"}
                onClick={() => handleDecision("no_avanza")}
              >
                No avanza
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Transcripción de la entrevista</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {interview.questions.length === 0 && (
                <p className="text-muted-foreground">Todavía no hay preguntas registradas.</p>
              )}
              {interview.questions.map((item, index) => (
                <div key={index} className="space-y-1 border-b border-border pb-3 last:border-0 last:pb-0">
                  <p className="text-sm font-medium">{item.question}</p>
                  <p className="text-xs text-muted-foreground">{formatDateTime(item.created_at)}</p>
                  {item.answer ? (
                    <p className="mt-1 rounded-md bg-secondary px-3 py-2 text-sm text-secondary-foreground">
                      {item.answer}
                    </p>
                  ) : (
                    <p className="mt-1 text-sm text-muted-foreground">Sin respuesta todavía.</p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
