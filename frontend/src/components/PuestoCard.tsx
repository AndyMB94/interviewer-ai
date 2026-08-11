import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Puesto } from "@/lib/api";

interface PuestoCardProps {
  puesto: Puesto;
  onSelect: (puesto: Puesto) => void;
}

export function PuestoCard({ puesto, onSelect }: PuestoCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-lg">
      <CardHeader>
        <CardTitle className="text-lg">{puesto.titulo}</CardTitle>
        <CardDescription className="line-clamp-3">{puesto.descripcion}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <p className="line-clamp-2 text-sm text-muted-foreground">
          <span className="font-medium text-foreground">Requisitos: </span>
          {puesto.requisitos}
        </p>
        <Button onClick={() => onSelect(puesto)} className="self-start">
          Postular a este puesto
        </Button>
      </CardContent>
    </Card>
  );
}
