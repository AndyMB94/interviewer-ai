import { useEffect, useState } from "react";
import { useSocket } from "../hooks/useSocket";
import { useMicrophone } from "../hooks/useMicrophone";
import { Header } from "../components/Header";
import { QuestionDisplay } from "../components/QuestionDisplay";
import { TextAnswerForm } from "../components/TextAnswerForm";
import { VoiceRecorder } from "../components/VoiceRecorder";

export function InterviewPage() {
  const { askQuestion, messages, sendAudio, isWaitingForResponse } = useSocket();
  const [question, setQuestion] = useState("");
  const [isFinished, setIsFinished] = useState(false);
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
    askQuestion(
      "Por favor, dame un resumen breve de mi desempeño en esta entrevista y una evaluación general de cómo me fue.",
    );
  };

  useEffect(() => {
    if (audioBlob) {
      sendAudio(audioBlob);
    }
  }, [audioBlob, sendAudio]);

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-2xl space-y-6 p-4">
        <Header />

        <QuestionDisplay
          messages={messages}
          isFinished={isFinished}
          isWaitingForResponse={isWaitingForResponse}
          onFinish={handleFinish}
        />

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
      </div>
    </div>
  );
}
