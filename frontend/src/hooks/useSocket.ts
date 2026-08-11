import { useCallback, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || "http://localhost:3000";

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  audioUrl?: string;
}

export function useSocket(token?: string) {
  const socketRef = useRef<Socket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

  useEffect(() => {
    const socket = io(GATEWAY_URL, token ? { auth: { token } } : undefined);
    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("conectado");
    });

    socket.on("ask", (response: string) => {
      setMessages((prev) => [...prev, { role: "assistant", text: response }]);
      setIsWaitingForResponse(false);
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
      setMessages((prev) => [...prev, { role: "user", text }]);
      setIsWaitingForResponse(true);
    });

    return () => {
      socket.disconnect();
    };
  }, [token]);

  const askQuestion = useCallback((question: string) => {
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setIsWaitingForResponse(true);
    socketRef.current?.emit("ask", question);
  }, []);

  const sendAudio = useCallback(async (blob: Blob) => {
    const buffer = await blob.arrayBuffer();
    socketRef.current?.emit("audio", buffer);
  }, []);

  const finishInterview = useCallback(() => {
    socketRef.current?.emit("finish");
  }, []);

  return { askQuestion, messages, sendAudio, isWaitingForResponse, finishInterview };
}