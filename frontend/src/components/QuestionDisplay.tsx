import { useEffect, useRef } from "react";
import { Bot } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import type { ChatMessage } from "@/hooks/useSocket";

function formatTime(date: Date) {
  return date.toLocaleTimeString("es-PE", { hour: "numeric", minute: "2-digit" });
}

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
  const { userEmail } = useAuth();

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
            <div className="flex items-start gap-2 self-start">
              <Avatar size="sm">
                <AvatarFallback>
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="max-w-[80%] rounded-lg bg-secondary px-4 py-2 text-secondary-foreground">
                ¡Hola! Soy Gaby, su entrevistadora técnica. Escríbame o grabe su voz cuando
                quiera empezar.
              </div>
            </div>
          )}

          {messages.map((message, index) => {
            const isAssistant = message.role === "assistant";
            return (
              <div
                key={index}
                className={`flex items-start gap-2 ${isAssistant ? "self-start" : "flex-row-reverse self-end"}`}
              >
                <Avatar size="sm">
                  <AvatarFallback>
                    {isAssistant ? (
                      <Bot className="h-4 w-4" />
                    ) : (
                      (userEmail?.[0]?.toUpperCase() ?? "?")
                    )}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    isAssistant
                      ? "bg-secondary text-secondary-foreground"
                      : "bg-primary text-primary-foreground"
                  }`}
                >
                  <p>{message.text}</p>
                  {message.audioUrl && (
                    <audio controls autoPlay src={message.audioUrl} className="mt-2 w-full" />
                  )}
                  <p
                    className={`mt-1 text-xs ${isAssistant ? "text-muted-foreground" : "text-primary-foreground/70"}`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            );
          })}

          {isWaitingForResponse && (
            <div className="flex items-start gap-2 self-start">
              <Avatar size="sm">
                <AvatarFallback>
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="rounded-lg bg-secondary px-4 py-2 text-secondary-foreground">
                <span className="inline-flex gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-current" />
                </span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {isFinished ? (
          <p className="mt-4 text-sm text-muted-foreground">
            Gracias por su tiempo — sus respuestas quedaron registradas. Nos vamos a poner en
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
