import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
    <Card>
      <CardHeader>
        <CardTitle>Responder por texto</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Input
            type="text"
            value={question}
            onChange={(e) => onQuestionChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") onSubmit();
            }}
          />
          <Button onClick={onSubmit}>Enviar</Button>
        </div>
      </CardContent>
    </Card>
  );
}
