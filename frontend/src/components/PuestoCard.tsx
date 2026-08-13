import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Puesto } from "@/lib/api";

const MODALIDAD_LABEL: Record<Puesto["modalidad"], string> = {
  presencial: "Presencial",
  remoto: "Remoto",
  hibrido: "Híbrido",
};

interface PuestoCardProps {
  puesto: Puesto;
}

export function PuestoCard({ puesto }: PuestoCardProps) {
  return (
    <Link to={`/puestos/${puesto.id}`} className="block">
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg">{puesto.titulo}</CardTitle>
            {puesto.categoria_nombre && (
              <Badge variant="secondary" className="shrink-0">
                {puesto.categoria_nombre}
              </Badge>
            )}
          </div>
          <CardDescription className="line-clamp-2">{puesto.descripcion}</CardDescription>
        </CardHeader>
        <CardContent>
          <Badge variant="outline">{MODALIDAD_LABEL[puesto.modalidad]}</Badge>
        </CardContent>
      </Card>
    </Link>
  );
}
