import { useEffect, useState } from "react";
import { useBlocker } from "react-router";
import { useSocket } from "../hooks/useSocket";
import { useMicrophone } from "../hooks/useMicrophone";
import { QuestionDisplay } from "../components/QuestionDisplay";
import { MessageComposer } from "../components/MessageComposer";
import { useAuth } from "../context/AuthContext";
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
import { Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { fetchMisPostulacionesPendientes, type MiPostulacion } from "@/lib/api";

export function InterviewPage() {
  const { accessToken } = useAuth();
  const { askQuestion, messages, sendAudio, isWaitingForResponse, finishInterview } = useSocket(
    accessToken ?? undefined,
  );
  const [question, setQuestion] = useState("");
  const [isFinished, setIsFinished] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [confirmandoFinalizar, setConfirmandoFinalizar] = useState(false);
  const [postulacionesPendientes, setPostulacionesPendientes] = useState<MiPostulacion[]>([]);
  const [postulacionesRestantes, setPostulacionesRestantes] = useState<MiPostulacion[]>([]);
  const [postulacionElegida, setPostulacionElegida] = useState<MiPostulacion | null>(null);
  // Con una sola postulación pendiente, se elige sola (sin mostrar el selector) -- Frontend 9.7.5.
  const miPostulacion =
    postulacionElegida ?? (postulacionesPendientes.length === 1 ? postulacionesPendientes[0] : null);
  const requiereElegirPuesto = postulacionesPendientes.length > 1 && !postulacionElegida;
  const {
    stream,
    error,
    requestPermission,
    isRecording,
    audioBlob,
    startRecording,
    stopRecording,
  } = useMicrophone();

  const handleSubmit = () => {
    if (!question.trim()) return;
    askQuestion(question, miPostulacion?.id);
    setQuestion("");
  };

  const handleFinish = () => {
    setIsFinished(true);
    finishInterview();
  };

  useEffect(() => {
    if (audioBlob) {
      sendAudio(audioBlob, miPostulacion?.id);
    }
  }, [audioBlob, sendAudio, miPostulacion]);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPostulacionesPendientes(accessToken)
      .then(setPostulacionesPendientes)
      .catch(() => setPostulacionesPendientes([]));
  }, [accessToken]);

  // Al terminar, se vuelve a consultar por si quedan otras postulaciones pendientes de
  // entrevistar -- sin esto, no hay forma visual de enterarse que hay que volver (Frontend 9.7.6).
  useEffect(() => {
    if (!isFinished || !accessToken) return;
    fetchMisPostulacionesPendientes(accessToken)
      .then(setPostulacionesRestantes)
      .catch(() => setPostulacionesRestantes([]));
  }, [isFinished, accessToken]);

  // Bloquea salir de una entrevista activa sin terminar (Frontend Fase 7.3) — evita perder el
  // progreso por un click accidental en el logo u otro link, ya que salir desconecta el socket.
  const entrevistaActivaSinTerminar = hasStarted && !isFinished;

  const blocker = useBlocker(entrevistaActivaSinTerminar);

  useEffect(() => {
    if (!entrevistaActivaSinTerminar) return;
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [entrevistaActivaSinTerminar]);

  if (!hasStarted && requiereElegirPuesto) {
    return (
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden p-4">
        <Card className="w-full max-w-2xl animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
          <CardHeader>
            <CardTitle>¿Para cuál puesto quiere hacer la entrevista?</CardTitle>
            <CardDescription>
              Tiene más de una postulación aprobada pendiente de entrevista — elija con cuál
              empezar.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {postulacionesPendientes.map((postulacion) => (
              <Button
                key={postulacion.id}
                variant="outline"
                className="justify-start"
                onClick={() => setPostulacionElegida(postulacion)}
              >
                {postulacion.puesto.titulo}
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!hasStarted) {
    return (
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden p-4">
        <Card className="w-full max-w-2xl animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
          <CardHeader className="items-center justify-items-center text-center">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>{miPostulacion ? `¡Hola, ${miPostulacion.nombre}!` : "¡Bienvenido!"}</CardTitle>
            <CardDescription>
              {miPostulacion
                ? `Va a tener una entrevista técnica para el puesto de ${miPostulacion.puesto.titulo}.`
                : "Va a tener una entrevista técnica con Gaby, nuestra entrevistadora de IA."}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-sm text-muted-foreground">
              Puede responder por texto o por voz — tómese el tiempo que necesite. Cuando esté
              listo/a, comenzamos.
            </p>
            <Button onClick={() => setHasStarted(true)} className="self-start">
              Empezar entrevista
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 p-4 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <QuestionDisplay
        messages={messages}
        isFinished={isFinished}
        isWaitingForResponse={isWaitingForResponse}
        onFinish={() => setConfirmandoFinalizar(true)}
      >
        {!isFinished && (
          <MessageComposer
            question={question}
            onQuestionChange={setQuestion}
            onSubmit={handleSubmit}
            stream={stream}
            error={error}
            requestPermission={requestPermission}
            isRecording={isRecording}
            startRecording={startRecording}
            stopRecording={stopRecording}
          />
        )}
      </QuestionDisplay>

      {isFinished && postulacionesRestantes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Tiene entrevistas pendientes</CardTitle>
            <CardDescription>
              Todavía tiene postulaciones aprobadas pendientes de entrevistar.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Recarga real de página (no navegación de React Router): la entrevista nueva
                necesita una conexión de socket nueva -- ver Frontend 9.7.6 en el roadmap. */}
            <Button nativeButton={false} render={<a href="/entrevista" />}>
              Continuar con mi próxima entrevista
            </Button>
          </CardContent>
        </Card>
      )}

      <AlertDialog
        open={blocker.state === "blocked"}
        onOpenChange={(open) => {
          if (!open && blocker.state === "blocked") blocker.reset();
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Seguro que quiere salir?</AlertDialogTitle>
            <AlertDialogDescription>
              Va a perder el progreso de esta entrevista.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (blocker.state === "blocked") blocker.proceed();
              }}
            >
              Salir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={confirmandoFinalizar} onOpenChange={setConfirmandoFinalizar}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Finalizar la entrevista?</AlertDialogTitle>
            <AlertDialogDescription>
              No va a poder responder más preguntas después de esto. Asegúrese de haber
              contestado todo lo que quería antes de continuar.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                setConfirmandoFinalizar(false);
                handleFinish();
              }}
            >
              Finalizar entrevista
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
