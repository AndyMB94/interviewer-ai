import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { PuestoSeccion } from "@/components/PuestoSeccion";
import { fetchPuesto, postularA, type Puesto } from "@/lib/api";
import { MODALIDAD_LABEL } from "@/lib/puesto";

export function PuestoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [puesto, setPuesto] = useState<Puesto | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchPuesto(Number(id))
      .then(setPuesto)
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!puesto || !cvFile) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await postularA({ puesto: puesto.id, nombre, email, cv: cvFile });
      setSubmitted(true);
    } catch (error) {
      setSubmitError((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 p-4 pt-8">
        <Skeleton className="h-8 w-32" />
        <Card>
          <CardHeader className="gap-2">
            <Skeleton className="h-7 w-2/3" />
            <Skeleton className="h-5 w-24" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loadError || !puesto) {
    return (
      <p className="mx-auto max-w-2xl p-4 pt-8 text-center text-destructive">
        {loadError ?? "No se encontró el puesto."}
      </p>
    );
  }

  if (submitted) {
    return (
      <div className="mx-auto max-w-md p-4 pt-8">
        <Card>
          <CardHeader>
            <CardTitle>¡Postulación enviada!</CardTitle>
            <CardDescription>
              Postuló a <span className="font-medium text-foreground">{puesto.titulo}</span>.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-sm text-muted-foreground">
              Un filtro con IA va a revisar su CV contra los requisitos del puesto. Si su perfil
              encaja, le vamos a mandar un email a <span className="font-medium">{email}</span> con
              los siguientes pasos.
            </p>
            <Button variant="outline" nativeButton={false} render={<Link to="/" />} className="self-start">
              Volver a vacantes
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4 pt-8 animate-in fade-in-0 slide-in-from-bottom-2 duration-300">
      <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/" />}>
        <ArrowLeft />
        Volver a vacantes
      </Button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-2xl">{puesto.titulo}</CardTitle>
            {puesto.categoria_nombre && <Badge variant="secondary">{puesto.categoria_nombre}</Badge>}
          </div>
          <Badge variant="outline" className="w-fit">
            {MODALIDAD_LABEL[puesto.modalidad]}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <PuestoSeccion titulo="Descripción del empleo" texto={puesto.descripcion} />
          <Separator />
          <PuestoSeccion titulo="Funciones" texto={puesto.funciones} />
          {puesto.funciones && <Separator />}
          <PuestoSeccion titulo="Requisitos" texto={puesto.requisitos} />
          <Separator />
          <PuestoSeccion titulo="Requisitos deseables" texto={puesto.requisitos_deseables} />

          {puesto.estado === "cerrado" ? (
            <p className="text-sm text-muted-foreground">
              Este puesto ya no está aceptando postulaciones.
            </p>
          ) : (
            !showForm && <Button onClick={() => setShowForm(true)}>Postular a este puesto</Button>
          )}
        </CardContent>
      </Card>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Complete sus datos</CardTitle>
            <CardDescription>Postulando a {puesto.titulo}.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="nombre" required>Nombre completo</Label>
                <Input
                  id="nombre"
                  autoComplete="name"
                  value={nombre}
                  onChange={(event) => setNombre(event.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email" required>Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="cv" required>CV (PDF)</Label>
                <Input
                  id="cv"
                  type="file"
                  accept="application/pdf"
                  onChange={(event) => setCvFile(event.target.files?.[0] ?? null)}
                  required
                />
              </div>

              {submitError && <p className="text-sm text-destructive">{submitError}</p>}

              <Button type="submit" disabled={submitting}>
                {submitting && <Spinner data-icon="inline-start" />}
                {submitting ? "Enviando..." : "Enviar postulación"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
