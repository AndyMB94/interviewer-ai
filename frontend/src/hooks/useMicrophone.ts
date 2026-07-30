import { useState } from "react";

export function useMicrophone() {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  const requestPermission = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setStream(mediaStream);
      setError(null);
    } catch (err) {
      setError("No se pudo acceder al micrófono");
      console.error(err);
    }
  };

  return { stream, error, requestPermission };
}