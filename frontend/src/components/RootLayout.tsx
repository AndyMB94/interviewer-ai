import { Outlet, useLocation } from "react-router";
import { Navbar } from "@/components/Navbar";
import { TooltipProvider } from "@/components/ui/tooltip";

export function RootLayout() {
  // El panel de reclutador arma su propia barra superior (con el botón del sidebar incluido) en
  // DashboardLayout, para no tener dos barras apiladas — acá no se repite el Navbar genérico.
  const { pathname } = useLocation();
  const isDashboard = pathname.startsWith("/dashboard");

  return (
    <TooltipProvider>
      <div className="flex min-h-screen flex-col">
        {!isDashboard && <Navbar />}
        <div className="relative flex min-w-0 flex-1 flex-col">
          <Outlet />
        </div>
      </div>
    </TooltipProvider>
  );
}
