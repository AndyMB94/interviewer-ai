import { useCallback, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || "http://localhost:3000";

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  audioUrl?: string;
  timestamp: Date;
}

// resumeInterviewId: undefined mientras todavía no se sabe si hay una entrevista para retomar
// (Fase 10.4/10.5) -- el socket espera a que se resuelva antes de conectar, para no arrancar una
// conexión "en blanco" y tener que reconectar apenas se sepa. null significa "ya se comprobó, no
// hay ninguna que retomar"; un número es el interview_id real a retomar.
export function useSocket(
  token: string | undefined,
  resumeInterviewId: number | null | undefined,
  initialMessages: ChatMessage[] = [],
  initialCreatedAt?: string,
) {
  const socketRef = useRef<Socket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  // Fase 10.7/10.8: siempre la hora real en que empezó la entrevista (nunca un cronómetro de
  // JavaScript que arranca de cero al montar) -- así el tiempo restante se calcula correctamente
  // incluso después de recargar la página.
  const [interviewStartedAt, setInterviewStartedAt] = useState<Date | null>(null);
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    if (resumeInterviewId === undefined) return;

    if (initialMessages.length > 0) setMessages(initialMessages);
    if (initialCreatedAt) setInterviewStartedAt(new Date(initialCreatedAt));

    const auth: { token?: string; interviewId?: number } = {};
    if (token) auth.token = token;
    if (resumeInterviewId) auth.interviewId = resumeInterviewId;

    const socket = io(GATEWAY_URL, Object.keys(auth).length > 0 ? { auth } : undefined);
    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("conectado");
    });

    socket.on("ask", (payload: { answer: string; createdAt?: string; timedOut?: boolean }) => {
      setMessages((prev) => [...prev, { role: "assistant", text: payload.answer, timestamp: new Date() }]);
      setIsWaitingForResponse(false);
      if (payload.createdAt) setInterviewStartedAt(new Date(payload.createdAt));
      if (payload.timedOut) setTimedOut(true);
    });

    socket.on("audio-response", (url: string) => {
      setMessages((prev) => {
        if (prev.length === 0) return prev;
        const updated = [...prev];
        updated[updated.length - 1] = { ...updated[updated.length - 1], audioUrl: url };
        return updated;
      });
    });

    socket.on("transcript", (text: string) => {
      setMessages((prev) => [...prev, { role: "user", text, timestamp: new Date() }]);
      setIsWaitingForResponse(true);
    });

    return () => {
      socket.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- initialMessages se lee una sola vez,
    // al resolverse resumeInterviewId; no debe disparar una reconexión si cambia de referencia.
  }, [token, resumeInterviewId]);

  const askQuestion = useCallback((question: string, postulacionId?: number) => {
    setMessages((prev) => [...prev, { role: "user", text: question, timestamp: new Date() }]);
    setIsWaitingForResponse(true);
    socketRef.current?.emit("ask", question, postulacionId);
  }, []);

  const sendAudio = useCallback(async (blob: Blob, postulacionId?: number) => {
    const buffer = await blob.arrayBuffer();
    socketRef.current?.emit("audio", buffer, postulacionId);
  }, []);

  const finishInterview = useCallback(() => {
    socketRef.current?.emit("finish");
  }, []);

  return {
    askQuestion,
    messages,
    sendAudio,
    isWaitingForResponse,
    finishInterview,
    interviewStartedAt,
    timedOut,
  };
}