import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { PuestoSeccion } from "@/components/PuestoSeccion";
import type { Puesto } from "@/lib/api";
import { MODALIDAD_LABEL } from "@/lib/puesto";

export function PuestoDetailSheet({
  puesto,
  onOpenChange,
}: {
  puesto: Puesto | null;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Sheet open={puesto !== null} onOpenChange={onOpenChange}>
      <SheetContent>
        {puesto && (
          <>
            <SheetHeader>
              <SheetTitle className="wrap-break-word">{puesto.titulo}</SheetTitle>
              <div className="flex flex-wrap gap-2 pt-1">
                <Badge variant={puesto.estado === "abierto" ? "default" : "secondary"}>
                  {puesto.estado}
                </Badge>
                <Badge variant="outline">{MODALIDAD_LABEL[puesto.modalidad]}</Badge>
                {puesto.categoria_nombre && <Badge variant="outline">{puesto.categoria_nombre}</Badge>}
              </div>
            </SheetHeader>
            <div className="flex flex-col gap-4 overflow-y-auto px-4 pb-4">
              <PuestoSeccion titulo="Descripción del empleo" texto={puesto.descripcion} />
              <Separator />
              <PuestoSeccion titulo="Funciones" texto={puesto.funciones} />
              {puesto.funciones && <Separator />}
              <PuestoSeccion titulo="Requisitos" texto={puesto.requisitos} />
              <Separator />
              <PuestoSeccion titulo="Requisitos deseables" texto={puesto.requisitos_deseables} />
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
