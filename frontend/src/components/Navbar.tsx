import { Link } from "react-router";
import { NavbarActions } from "@/components/NavbarActions";
import { useAuth } from "@/context/AuthContext";

export function Navbar() {
  const { roles } = useAuth();

  // El logo lleva de vuelta a la pantalla principal de cada rol, no siempre a "/" — un Reclutador
  // no quiere terminar en la grilla pública, y un Postulante necesita cómo volver a su entrevista.
  const logoDestination = roles.includes("Reclutador")
    ? "/dashboard"
    : roles.includes("Postulante")
      ? "/entrevista"
      : "/";

  return (
    <nav className="sticky top-0 border-b border-border bg-background/80 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto flex max-w-4xl items-center justify-between p-4">
        <Link to={logoDestination} className="font-bold">
          Vacantia
        </Link>
        <NavbarActions />
      </div>
    </nav>
  );
}
