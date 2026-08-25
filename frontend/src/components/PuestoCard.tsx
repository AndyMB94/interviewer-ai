import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Puesto } from "@/lib/api";
import { MODALIDAD_LABEL } from "@/lib/puesto";

interface PuestoCardProps {
  puesto: Puesto;
}

export function PuestoCard({ puesto }: PuestoCardProps) {
  return (
    <Link to={`/puestos/${puesto.id}`} className="block h-full">
      <Card className="h-full transition-all hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10">
        <CardHeader>
          {puesto.categoria_nombre && (
            <div className="flex justify-end">
              <Badge variant="secondary">{puesto.categoria_nombre}</Badge>
            </div>
          )}
          <CardTitle className="line-clamp-2 wrap-break-word text-lg">{puesto.titulo}</CardTitle>
          <CardDescription className="line-clamp-2 wrap-break-word">{puesto.descripcion}</CardDescription>
        </CardHeader>
        <CardContent className="mt-auto">
          <Badge variant="outline">{MODALIDAD_LABEL[puesto.modalidad]}</Badge>
        </CardContent>
      </Card>
    </Link>
  );
}
