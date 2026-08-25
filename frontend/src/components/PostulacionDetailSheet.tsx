import { FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { PuestoSeccion } from "@/components/PuestoSeccion";
import type { Postulacion } from "@/lib/api";

const ESTADO_VARIANT: Record<Postulacion["estado"], "outline" | "default" | "destructive"> = {
  pendiente: "outline",
  aprobado: "default",
  rechazado: "destructive",
};

export function PostulacionDetailSheet({
  postulacion,
  onOpenChange,
}: {
  postulacion: Postulacion | null;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Sheet open={postulacion !== null} onOpenChange={onOpenChange}>
      <SheetContent>
        {postulacion && (
          <>
            <SheetHeader>
              <SheetTitle className="min-w-0 wrap-break-word">{postulacion.nombre}</SheetTitle>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <Badge variant={ESTADO_VARIANT[postulacion.estado]}>{postulacion.estado}</Badge>
                <span className="min-w-0 truncate text-sm text-muted-foreground">
                  {postulacion.email}
                </span>
              </div>
            </SheetHeader>
            <div className="flex flex-col gap-4 overflow-y-auto px-4 pb-4">
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<a href={postulacion.cv} target="_blank" rel="noopener noreferrer" />}
                className="w-fit"
              >
                <FileText className="h-4 w-4" />
                Ver CV
              </Button>
              <PuestoSeccion titulo="Puesto" texto={postulacion.puesto_titulo} />
              <Separator />
              <PuestoSeccion
                titulo="Resultado del filtro de CV"
                texto={postulacion.resultado_filtro || "Sin resultado registrado."}
              />
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
