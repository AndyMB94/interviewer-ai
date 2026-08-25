import type { LucideIcon } from "lucide-react";

export function PuestoSeccion({
  titulo,
  texto,
  icon: Icon,
}: {
  titulo: string;
  texto: string;
  icon?: LucideIcon;
}) {
  if (!texto) return null;
  return (
    <div className="space-y-1">
      <h2 className="flex items-center gap-1.5 font-semibold">
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        {titulo}
      </h2>
      <p className="whitespace-pre-line text-sm text-muted-foreground">{texto}</p>
    </div>
  );
}
