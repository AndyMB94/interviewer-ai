import { useEffect, useRef, useState } from "react";

export function useMicrophone() {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

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

  const startRecording = () => {
    if (!stream) return;

    chunksRef.current = [];
    const mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      chunksRef.current.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      setAudioBlob(blob);
    };

    mediaRecorder.start();
    mediaRecorderRef.current = mediaRecorder;
    setIsRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  // Detener la grabación (MediaRecorder) no suelta el permiso del micrófono en sí -- el
  // navegador sigue mostrando el ícono de "grabando" hasta que se llama .stop() en cada track
  // del MediaStream. Sin esto, el micrófono queda activo indefinidamente (incluso después de
  // finalizar la entrevista o cerrar sesión) hasta que se cierra la pestaña del todo.
  const releaseMicrophone = () => {
    stream?.getTracks().forEach((track) => track.stop());
    setStream(null);
  };

  useEffect(() => {
    return () => {
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [stream]);

  return {
    stream,
    error,
    requestPermission,
    isRecording,
    audioBlob,
    startRecording,
    stopRecording,
    releaseMicrophone,
  };
}