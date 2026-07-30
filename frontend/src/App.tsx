import { useState } from "react";
import { useSocket } from "./hooks/useSocket";
import { useMicrophone } from "./hooks/useMicrophone";

function App() {
  const { askQuestion, answer } = useSocket();
  const [question, setQuestion] = useState("");
  const { stream, error, requestPermission } = useMicrophone();

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
    </div>
  );
}

export default App;