import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChatMessage } from "@/hooks/useSocket";

interface QuestionDisplayProps {
  messages: ChatMessage[];
  isFinished: boolean;
  isWaitingForResponse: boolean;
  onFinish: () => void;
}

export function QuestionDisplay({
  messages,
  isFinished,
  isWaitingForResponse,
  onFinish,
}: QuestionDisplayProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isWaitingForResponse]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{isFinished ? "Feedback final" : "Entrevista"}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex max-h-112 flex-col gap-3 overflow-y-auto">
          {messages.length === 0 && (
            <div className="max-w-[80%] self-start rounded-lg bg-secondary px-4 py-2 text-secondary-foreground">
              ¡Hola! Soy Gaby, tu entrevistadora técnica. Escribime o grabá tu voz cuando
              quieras empezar.
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === "assistant"
                  ? "self-start bg-secondary text-secondary-foreground"
                  : "self-end bg-primary text-primary-foreground"
              }`}
            >
              <p>{message.text}</p>
              {message.audioUrl && (
                <audio controls autoPlay src={message.audioUrl} className="mt-2 w-full" />
              )}
            </div>
          ))}

          {isWaitingForResponse && (
            <div className="self-start rounded-lg bg-secondary px-4 py-2 text-secondary-foreground">
              <span className="inline-flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-current" />
              </span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {isFinished ? (
          <p className="mt-4 text-sm text-muted-foreground">
            Gracias por tu tiempo — tus respuestas quedaron registradas. Nos vamos a poner en
            contacto por email con los siguientes pasos.
          </p>
        ) : (
          <Button className="mt-4" onClick={onFinish}>
            Finalizar entrevista
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
