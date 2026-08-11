import { useEffect, useState } from "react";
import { useSocket } from "../hooks/useSocket";
import { useMicrophone } from "../hooks/useMicrophone";
import { QuestionDisplay } from "../components/QuestionDisplay";
import { TextAnswerForm } from "../components/TextAnswerForm";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { useAuth } from "../context/AuthContext";

export function InterviewPage() {
  const { accessToken } = useAuth();
  const { askQuestion, messages, sendAudio, isWaitingForResponse, finishInterview } = useSocket(
    accessToken ?? undefined,
  );
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
    finishInterview();
  };

  useEffect(() => {
    if (audioBlob) {
      sendAudio(audioBlob);
    }
  }, [audioBlob, sendAudio]);

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
