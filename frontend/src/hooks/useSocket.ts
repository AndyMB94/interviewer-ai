import { useCallback, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const GATEWAY_URL = "http://localhost:3000";

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);
  const [audioResponseUrl, setAudioResponseUrl] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);

  useEffect(() => {
    const socket = io(GATEWAY_URL);
    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("conectado");
    });

    socket.on("ask", (response: string) => {
      setAnswer(response);
    });

    socket.on("audio-response", (url: string) => {
      setAudioResponseUrl(url);
    });

    socket.on("transcript", (text: string) => {
      setTranscript(text);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const askQuestion = useCallback((question: string) => {
    socketRef.current?.emit("ask", question);
  }, []);

  const sendAudio = useCallback(async (blob: Blob) => {
    const buffer = await blob.arrayBuffer();
    socketRef.current?.emit("audio", buffer);
  }, []);

  return { askQuestion, answer, sendAudio, audioResponseUrl, transcript };
}