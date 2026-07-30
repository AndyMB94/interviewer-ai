import { useState } from "react";
import { useSocket } from "./hooks/useSocket";
import { useMicrophone } from "./hooks/useMicrophone";

function App() {
  const { askQuestion, answer } = useSocket();
  const [question, setQuestion] = useState("");
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

  return (
    <div>
      <h1>Interviewer AI</h1>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={handleSubmit}>Enviar</button>
      {answer && <p>{answer}</p>}

      <hr />

      <button onClick={requestPermission}>Permitir micrófono</button>
      {stream && <p>Micrófono habilitado ✅</p>}
      {error && <p>{error}</p>}

      {stream && (
        <button onClick={isRecording ? stopRecording : startRecording}>
          {isRecording ? "Detener" : "Grabar"}
        </button>
      )}

      {audioBlob && <audio controls src={URL.createObjectURL(audioBlob)} />}
    </div>
  );
}

export default App;