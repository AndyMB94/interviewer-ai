import { Button } from "@/components/ui/button";

interface QuestionDisplayProps {
  answer: string | null;
  audioResponseUrl: string | null;
  isFinished: boolean;
  onFinish: () => void;
}

export function QuestionDisplay({
  answer,
  audioResponseUrl,
  isFinished,
  onFinish,
}: QuestionDisplayProps) {
  return (
    <section className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">
        {isFinished ? "Feedback final" : "Pregunta actual"}
      </h2>
      <p>{answer ?? "Todavía no hay ninguna pregunta."}</p>
      {audioResponseUrl && <audio controls autoPlay src={audioResponseUrl} />}
      <Button onClick={onFinish}>Finalizar entrevista</Button>
    </section>
  );
}
