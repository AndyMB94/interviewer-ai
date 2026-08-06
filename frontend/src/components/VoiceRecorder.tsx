import { CheckCircle2, CircleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface VoiceRecorderProps {
  stream: MediaStream | null;
  error: string | null;
  requestPermission: () => void;
  isRecording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
}

export function VoiceRecorder({
  stream,
  error,
  requestPermission,
  isRecording,
  startRecording,
  stopRecording,
}: VoiceRecorderProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Responder por voz</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {!stream && <Button onClick={requestPermission}>Permitir micrófono</Button>}
        {stream && (
          <p className="flex items-center gap-1 text-sm text-muted-foreground">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            Micrófono habilitado
          </p>
        )}
        {error && (
          <p className="flex items-center gap-1 text-sm text-destructive">
            <CircleAlert className="h-4 w-4" />
            {error}
          </p>
        )}

        {stream && (
          <div className="flex items-center gap-2">
            <Button
              variant={isRecording ? "destructive" : "default"}
              onClick={isRecording ? stopRecording : startRecording}
            >
              {isRecording ? "Detener" : "Grabar"}
            </Button>
            {isRecording && (
              <span className="flex items-center gap-1 text-sm text-destructive">
                <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
                Grabando...
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
