import { Button } from "@/components/ui/button";

interface VoiceRecorderProps {
  stream: MediaStream | null;
  error: string | null;
  requestPermission: () => void;
  isRecording: boolean;
  audioBlob: Blob | null;
  startRecording: () => void;
  stopRecording: () => void;
  transcript: string | null;
}

export function VoiceRecorder({
  stream,
  error,
  requestPermission,
  isRecording,
  audioBlob,
  startRecording,
  stopRecording,
  transcript,
}: VoiceRecorderProps) {
  return (
    <section className="p-4 space-y-2">
      <h3 className="text-lg font-medium">Responder por voz</h3>
      <Button onClick={requestPermission}>Permitir micrófono</Button>
      {stream && <p>Micrófono habilitado ✅</p>}
      {error && <p>{error}</p>}

      {stream && (
        <Button onClick={isRecording ? stopRecording : startRecording}>
          {isRecording ? "Detener" : "Grabar"}
        </Button>
      )}

      {audioBlob && <audio controls src={URL.createObjectURL(audioBlob)} />}
      {transcript && <p>Transcripción: "{transcript}"</p>}
    </section>
  );
}
