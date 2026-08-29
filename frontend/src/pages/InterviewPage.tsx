import { useEffect, useRef, useState } from "react";
import { useBlocker, useNavigate } from "react-router";
import { useSocket, type ChatMessage } from "../hooks/useSocket";
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
import { toast } from "@/components/ui/toast";
import { fetchInterviewEnCurso, fetchMisPostulacionesPendientes, type MiPostulacion } from "@/lib/api";

const DURACION_ENTREVISTA_SEGUNDOS = 30 * 60;
const AVISO_MINUTOS_RESTANTES = 5;

function formatTiempoRestante(segundos: number) {
  const minutos = Math.floor(segundos / 60);
  const restoSegundos = segundos % 60;
  return `${minutos}:${restoSegundos.toString().padStart(2, "0")}`;
}

export function InterviewPage() {
  const { accessToken, logout } = useAuth();
  const navigate = useNavigate();
  // Fase 11.6: distingue "todavía no se sabe" de "ya se comprobó y no tiene ninguna" -- sin
  // esto no se puede decidir con seguridad cuándo redirigir sin postulaciones reales.
  const [postulacionesCargadas, setPostulacionesCargadas] = useState(false);
  // undefined mientras se comprueba si hay una entrevista sin terminar (Fase 10.4/10.5); null
  // significa "ya se comprobó, no hay ninguna"; un número es el interview_id a retomar.
  const [resumeInterviewId, setResumeInterviewId] = useState<number | null | undefined>(undefined);
  const [historialPrevio, setHistorialPrevio] = useState<ChatMessage[]>([]);
  const [createdAtPrevio, setCreatedAtPrevio] = useState<string | undefined>(undefined);
  const [puestoEnCurso, setPuestoEnCurso] = useState<string | null>(null);
  const {
    askQuestion,
    messages,
    sendAudio,
    isWaitingForResponse,
    finishInterview,
    interviewStartedAt,
    timedOut,
  } = useSocket(accessToken ?? undefined, resumeInterviewId, historialPrevio, createdAtPrevio);
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
    releaseMicrophone,
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

  // Fase 10.7/10.8: cronómetro en tiempo real, calculado siempre contra la hora real del backend
  // (interviewStartedAt) -- nunca un contador que arranque de cero al recargar la página.
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const avisoMostradoRef = useRef(false);

  useEffect(() => {
    if (!interviewStartedAt) {
      setSecondsLeft(null);
      return;
    }
    const tick = () => {
      const transcurridos = (Date.now() - interviewStartedAt.getTime()) / 1000;
      setSecondsLeft(Math.max(0, Math.round(DURACION_ENTREVISTA_SEGUNDOS - transcurridos)));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [interviewStartedAt]);

  // Aviso único (toast, no un alert nativo) cuando quedan 5 minutos o menos.
  useEffect(() => {
    if (!hasStarted || secondsLeft === null || secondsLeft <= 0 || avisoMostradoRef.current) return;
    if (secondsLeft <= AVISO_MINUTOS_RESTANTES * 60) {
      avisoMostradoRef.current = true;
      toast.add({
        type: "warning",
        title: `Le quedan ${AVISO_MINUTOS_RESTANTES} minutos para finalizar la entrevista.`,
      });
    }
  }, [secondsLeft, hasStarted]);

  // Fase 10.9: si el backend avisa que se acabó el tiempo (respaldo por si el cronómetro local
  // no llegó a dispararse), la pantalla pasa a "finalizada" igual que con el botón manual.
  useEffect(() => {
    if (timedOut) setIsFinished(true);
  }, [timedOut]);

  // Suelta el micrófono apenas termina la entrevista (manual o por tiempo) -- ya no se puede
  // grabar nada más, no tiene sentido dejarlo activo mientras se decide si vuelve al selector
  // o se cierra la sesión.
  useEffect(() => {
    if (isFinished) releaseMicrophone();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- releaseMicrophone no está
    // memoizada; solo debe dispararse cuando isFinished cambia, no en cada render.
  }, [isFinished]);

  // Fase 10.10: al llegar a cero, el propio frontend dispara "Finalizar entrevista" en vez de
  // esperar a que el siguiente mensaje falle contra el corte del backend.
  useEffect(() => {
    if (secondsLeft === 0 && hasStarted && !isFinished) {
      handleFinish();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- handleFinish no está memoizado;
    // solo debe dispararse cuando el cronómetro llega exactamente a cero (o cuando hasStarted
    // pasa a true si el tiempo ya se había agotado mientras esperaba en la confirmación).
  }, [secondsLeft, hasStarted]);

  useEffect(() => {
    if (audioBlob) {
      sendAudio(audioBlob, miPostulacion?.id);
    }
  }, [audioBlob, sendAudio, miPostulacion]);

  useEffect(() => {
    if (!accessToken) return;
    fetchMisPostulacionesPendientes(accessToken)
      .then(setPostulacionesPendientes)
      .catch(() => setPostulacionesPendientes([]))
      .finally(() => setPostulacionesCargadas(true));
  }, [accessToken]);

  // Fase 11.6: sin ninguna postulación real (ni pendiente de entrevistar, ni una en curso para
  // retomar), esta pantalla no tiene nada legítimo que ofrecer -- antes mostraba una bienvenida
  // genérica que ya no puede funcionar (Fase 11.3, `ask` exige postulacion_id siempre).
  useEffect(() => {
    if (hasStarted || !postulacionesCargadas || resumeInterviewId === undefined) return;
    if (postulacionesPendientes.length === 0 && !resumeInterviewId) {
      toast.add({
        type: "error",
        title: "No tiene ninguna postulación aprobada pendiente de entrevistar.",
      });
      navigate("/");
    }
  }, [hasStarted, postulacionesCargadas, resumeInterviewId, postulacionesPendientes, navigate]);

  // Fase 10.4/10.5: si cerró el navegador a medio camino, esto detecta la entrevista sin
  // terminar y arma el historial real para retomarla -- en vez de que el socket, sin saberlo,
  // intente crear una entrevista nueva y choque con la que ya existe.
  useEffect(() => {
    if (!accessToken) return;
    fetchInterviewEnCurso(accessToken)
      .then((enCurso) => {
        if (!enCurso) {
          setResumeInterviewId(null);
          return;
        }
        const mensajes: ChatMessage[] = [];
        for (const q of enCurso.questions) {
          mensajes.push({ role: "user", text: q.question, timestamp: new Date(q.created_at) });
          if (q.answer !== null) {
            mensajes.push({
              role: "assistant",
              text: q.answer,
              timestamp: new Date(q.answered_at ?? q.created_at),
            });
          }
        }
        setHistorialPrevio(mensajes);
        setCreatedAtPrevio(enCurso.created_at);
        setPuestoEnCurso(enCurso.puesto_titulo);
        setResumeInterviewId(enCurso.interview_id);
      })
      .catch(() => setResumeInterviewId(null));
  }, [accessToken]);

  // Al terminar, se vuelve a consultar por si quedan otras postulaciones pendientes de
  // entrevistar -- sin esto, no hay forma visual de enterarse que hay que volver (Frontend 9.7.6).
  // Fase 10.12: si no le queda ninguna, la sesión se cierra de verdad (logout real, no solo
  // visual) -- la cuenta del postulante ya cumplió su propósito, no debería quedar abierta.
  useEffect(() => {
    if (!isFinished || !accessToken) return;
    fetchMisPostulacionesPendientes(accessToken)
      .then((restantes) => {
        setPostulacionesRestantes(restantes);
        if (restantes.length === 0) {
          logout();
        }
      })
      .catch(() => setPostulacionesRestantes([]));
  }, [isFinished, accessToken, logout]);

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

  if (!hasStarted && resumeInterviewId) {
    return (
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden p-4">
        <Card className="w-full max-w-2xl animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
          <CardHeader>
            <CardTitle>¿Desea continuar con su entrevista en curso?</CardTitle>
            <CardDescription>
              Tiene una entrevista sin terminar
              {puestoEnCurso ? ` para el puesto de ${puestoEnCurso}` : ""}. Al continuar, retoma
              exactamente donde la dejó — no se pierde nada de lo ya conversado.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setHasStarted(true)} className="self-start">
              Continuar entrevista
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

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
        tiempoRestante={!isFinished && secondsLeft !== null ? formatTiempoRestante(secondsLeft) : undefined}
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
