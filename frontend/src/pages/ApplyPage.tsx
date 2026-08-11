import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PuestoCard } from "@/components/PuestoCard";
import { fetchPuestosAbiertos, postularA, type Puesto } from "@/lib/api";

export function ApplyPage() {
  const [puestos, setPuestos] = useState<Puesto[]>([]);
  const [loadingPuestos, setLoadingPuestos] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [selectedPuesto, setSelectedPuesto] = useState<Puesto | null>(null);
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    fetchPuestosAbiertos()
      .then(setPuestos)
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoadingPuestos(false));
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedPuesto || !cvFile) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await postularA({ puesto: selectedPuesto.id, nombre, email, cv: cvFile });
      setSubmitted(true);
    } catch (error) {
      setSubmitError((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  const resetFlow = () => {
    setSelectedPuesto(null);
    setNombre("");
    setEmail("");
    setCvFile(null);
    setSubmitted(false);
    setSubmitError(null);
  };

  if (submitted && selectedPuesto) {
    return (
      <div className="mx-auto max-w-md p-4 pt-8">
        <Card>
          <CardHeader>
            <CardTitle>¡Postulación enviada!</CardTitle>
            <CardDescription>
              Postulaste a <span className="font-medium text-foreground">{selectedPuesto.titulo}</span>.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-sm text-muted-foreground">
              Un filtro con IA va a revisar tu CV contra los requisitos del puesto. Si tu perfil
              encaja, te vamos a mandar un email a <span className="font-medium">{email}</span> con
              los siguientes pasos.
            </p>
            <Button variant="outline" onClick={resetFlow} className="self-start">
              Postular a otro puesto
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (selectedPuesto) {
    return (
      <div className="mx-auto max-w-md space-y-4 p-4 pt-8">
        <Button variant="ghost" size="sm" onClick={() => setSelectedPuesto(null)}>
          ‹ Elegir otro puesto
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>{selectedPuesto.titulo}</CardTitle>
            <CardDescription>Completá tus datos para postular.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="nombre">Nombre completo</Label>
                <Input
                  id="nombre"
                  value={nombre}
                  onChange={(event) => setNombre(event.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="cv">CV (PDF)</Label>
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
                {submitting ? "Enviando..." : "Enviar postulación"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-4 pt-8">
      <header className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">Vacantes abiertas</h1>
        <p className="text-muted-foreground">
          Elegí un puesto y postulá subiendo tu CV — sin necesidad de crear una cuenta.
        </p>
      </header>

      {loadingPuestos && <p className="text-center text-muted-foreground">Cargando puestos...</p>}

      {loadError && <p className="text-center text-destructive">{loadError}</p>}

      {!loadingPuestos && !loadError && puestos.length === 0 && (
        <p className="text-center text-muted-foreground">
          No hay vacantes abiertas por el momento. Volvé a intentarlo más adelante.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {puestos.map((puesto) => (
          <PuestoCard key={puesto.id} puesto={puesto} onSelect={setSelectedPuesto} />
        ))}
      </div>
    </div>
  );
}
