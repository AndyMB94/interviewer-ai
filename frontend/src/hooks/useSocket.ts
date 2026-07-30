import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GATEWAY_URL = "http://localhost:3000";

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);

  useEffect(() => {
    const socket = io(GATEWAY_URL);
    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("conectado");
    });

    socket.on("ask", (response: string) => {
      setAnswer(response);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const askQuestion = (question: string) => {
    socketRef.current?.emit("ask", question);
  };

  return { askQuestion, answer };
}
