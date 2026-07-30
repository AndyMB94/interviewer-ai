import { useSocket } from "./hooks/useSocket";

function App() {
  useSocket();

  return <h1>Interviewer AI</h1>;
}

export default App;