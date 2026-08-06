import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface TextAnswerFormProps {
  question: string;
  onQuestionChange: (value: string) => void;
  onSubmit: () => void;
}

export function TextAnswerForm({
  question,
  onQuestionChange,
  onSubmit,
}: TextAnswerFormProps) {
  return (
    <section className="p-4 space-y-2">
      <h3 className="text-lg font-medium">Responder por texto</h3>
      <div className="flex gap-2">
        <Input
          type="text"
          value={question}
          onChange={(e) => onQuestionChange(e.target.value)}
        />
        <Button onClick={onSubmit}>Enviar</Button>
      </div>
    </section>
  );
}
