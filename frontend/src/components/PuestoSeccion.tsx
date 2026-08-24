export function PuestoSeccion({ titulo, texto }: { titulo: string; texto: string }) {
  if (!texto) return null;
  return (
    <div className="space-y-1">
      <h2 className="font-semibold">{titulo}</h2>
      <p className="whitespace-pre-line text-sm text-muted-foreground">{texto}</p>
    </div>
  );
}
