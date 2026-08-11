import { Navigate } from "react-router";
import { RequireAuth } from "@/components/RequireAuth";
import { useAuth } from "@/context/AuthContext";

function RoleGate({ role, children }: { role: string; children: React.ReactNode }) {
  const { roles } = useAuth();

  if (!roles.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export function RequireRole({ role, children }: { role: string; children: React.ReactNode }) {
  return (
    <RequireAuth>
      <RoleGate role={role}>{children}</RoleGate>
    </RequireAuth>
  );
}
