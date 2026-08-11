import { useEffect, useState } from "react";
import { useSocket } from "../hooks/useSocket";
import { useMicrophone } from "../hooks/useMicrophone";
import { QuestionDisplay } from "../components/QuestionDisplay";
import { TextAnswerForm } from "../components/TextAnswerForm";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { useAuth } from "../context/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { fetchMiPostulacion, type MiPostulacion } from "@/lib/api";

export function InterviewPage() {
  const { accessToken } = useAuth();
  const { askQuestion, messages, sendAudio, isWaitingForResponse, finishInterview } = useSocket(
    accessToken ?? undefined,
  );
  const [question, setQuestion] = useState("");
  const [isFinished, setIsFinished] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [miPostulacion, setMiPostulacion] = useState<MiPostulacion | null>(null);
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
    askQuestion(question);
    setQuestion("");
  };

  const handleFinish = () => {
    setIsFinished(true);
    finishInterview();
  };

  useEffect(() => {
    if (audioBlob) {
      sendAudio(audioBlob);
    }
  }, [audioBlob, sendAudio]);

  useEffect(() => {
    if (!accessToken) return;
    fetchMiPostulacion(accessToken)
      .then(setMiPostulacion)
      .catch(() => setMiPostulacion(null));
  }, [accessToken]);

  if (!hasStarted) {
    return (
      <div className="mx-auto max-w-2xl p-4">
        <Card>
          <CardHeader>
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
    <div className="mx-auto max-w-2xl space-y-6 p-4">
      <QuestionDisplay
        messages={messages}
        isFinished={isFinished}
        isWaitingForResponse={isWaitingForResponse}
        onFinish={handleFinish}
      />

      {!isFinished && (
        <>
          <TextAnswerForm
            question={question}
            onQuestionChange={setQuestion}
            onSubmit={handleSubmit}
          />

          <VoiceRecorder
            stream={stream}
            error={error}
            requestPermission={requestPermission}
            isRecording={isRecording}
            startRecording={startRecording}
            stopRecording={stopRecording}
          />
        </>
      )}
    </div>
  );
}
