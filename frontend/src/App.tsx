import { useState } from "react";
import { useSocket } from "./hooks/useSocket";

function App() {
  const { askQuestion, answer } = useSocket();
  const [question, setQuestion] = useState("");

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
    </div>
  );
}

export default App;