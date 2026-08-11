import { Navigate } from "react-router";
import { useAuth } from "@/context/AuthContext";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isCheckingSession } = useAuth();

  // Espera el silent refresh (Fase P.7) antes de decidir — si no, redirigiría a /login de una,
  // incluso cuando la cookie del refresh token todavía es válida.
  if (isCheckingSession) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
