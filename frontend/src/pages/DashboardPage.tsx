import { useAuth } from "@/context/AuthContext";

export function DashboardPage() {
  const { userEmail } = useAuth();

  return (
    <div className="mx-auto max-w-4xl p-4">
      <h1 className="text-2xl font-bold">Panel de reclutador</h1>
      <p className="mt-2 text-muted-foreground">
        Sesión iniciada como {userEmail}. El contenido real (puestos, postulaciones) se agrega en
        Frontend Fase 6.2.
      </p>
    </div>
  );
}
