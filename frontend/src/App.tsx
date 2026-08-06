import { useEffect, useState } from "react";
import { useSocket } from "./hooks/useSocket";
import { useMicrophone } from "./hooks/useMicrophone";
import { Header } from "./components/Header";
import { QuestionDisplay } from "./components/QuestionDisplay";
import { TextAnswerForm } from "./components/TextAnswerForm";
import { VoiceRecorder } from "./components/VoiceRecorder";

function App() {
  const { askQuestion, answer, sendAudio, audioResponseUrl, transcript } = useSocket();
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
    askQuestion(question);
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
    <div>
      <Header />

      <QuestionDisplay
        answer={answer}
        audioResponseUrl={audioResponseUrl}
        isFinished={isFinished}
        onFinish={handleFinish}
      />

      <hr />

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
        audioBlob={audioBlob}
        startRecording={startRecording}
        stopRecording={stopRecording}
        transcript={transcript}
      />
    </div>
  );
}

export default App;