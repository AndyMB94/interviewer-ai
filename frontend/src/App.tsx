import { useEffect, useState } from "react";
import { useSocket } from "./hooks/useSocket";
import { useMicrophone } from "./hooks/useMicrophone";

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
      <h1>Interviewer AI</h1>

      <section>
        <h2>{isFinished ? "Feedback final" : "Pregunta actual"}</h2>
        {answer ? <p>{answer}</p> : <p>Todavía no hay ninguna pregunta.</p>}
        {audioResponseUrl && <audio controls autoPlay src={audioResponseUrl} />}
      </section>

      <button onClick={handleFinish}>Finalizar entrevista</button>

      <hr />

      <section>
        <h3>Responder por texto</h3>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleSubmit}>Enviar</button>
      </section>

      <section>
        <h3>Responder por voz</h3>
        <button onClick={requestPermission}>Permitir micrófono</button>
        {stream && <p>Micrófono habilitado ✅</p>}
        {error && <p>{error}</p>}

        {stream && (
          <button onClick={isRecording ? stopRecording : startRecording}>
            {isRecording ? "Detener" : "Grabar"}
          </button>
        )}

        {audioBlob && <audio controls src={URL.createObjectURL(audioBlob)} />}
        {transcript && <p>Transcripción: "{transcript}"</p>}
      </section>
    </div>
  );
}

export default App;