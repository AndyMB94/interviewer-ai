import { CircleAlert, Mic, Send, Square } from "lucide-react";
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput } from "@/components/ui/input-group";

interface MessageComposerProps {
  question: string;
  onQuestionChange: (value: string) => void;
  onSubmit: () => void;
  stream: MediaStream | null;
  error: string | null;
  requestPermission: () => void;
  isRecording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
}

export function MessageComposer({
  question,
  onQuestionChange,
  onSubmit,
  stream,
  error,
  requestPermission,
  isRecording,
  startRecording,
  stopRecording,
}: MessageComposerProps) {
  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else if (!stream) {
      requestPermission();
    } else {
      startRecording();
    }
  };

  return (
    <div className="space-y-1">
      <InputGroup>
        <InputGroupInput
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") onSubmit();
          }}
          placeholder="Escriba su respuesta..."
        />
        <InputGroupAddon align="inline-end">
          <InputGroupButton
            variant={isRecording ? "destructive" : "ghost"}
            size="icon-sm"
            onClick={handleMicClick}
            aria-label={isRecording ? "Detener grabación" : "Grabar audio"}
          >
            {isRecording ? <Square /> : <Mic />}
          </InputGroupButton>
          <InputGroupButton size="icon-sm" onClick={onSubmit} aria-label="Enviar">
            <Send />
          </InputGroupButton>
        </InputGroupAddon>
      </InputGroup>

      {(isRecording || error) && (
        <div className="flex items-center gap-3 px-1 text-xs">
          {isRecording && (
            <span className="flex items-center gap-1 text-destructive">
              <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
              Grabando...
            </span>
          )}
          {error && (
            <span className="flex items-center gap-1 text-destructive">
              <CircleAlert className="h-3 w-3" />
              {error}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
