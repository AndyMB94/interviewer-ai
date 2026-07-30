import { useEffect, useRef } from "react";
import { io, Socket } from "socket.io-client";

const GATEWAY_URL = "http://localhost:3000";

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(GATEWAY_URL);
    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("conectado");
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return socketRef;
}