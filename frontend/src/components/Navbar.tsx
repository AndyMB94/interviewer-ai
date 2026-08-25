import { Moon, Sun } from "lucide-react";
import { Link, useNavigate } from "react-router";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/hooks/useTheme";

export function Navbar() {
  const { isAuthenticated, userEmail, roles, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  // El logo lleva de vuelta a la pantalla principal de cada rol, no siempre a "/" — un Reclutador
  // no quiere terminar en la grilla pública, y un Postulante necesita cómo volver a su entrevista.
  const logoDestination = roles.includes("Reclutador")
    ? "/dashboard"
    : roles.includes("Postulante")
      ? "/entrevista"
      : "/";

  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto flex max-w-4xl items-center justify-between p-4">
        <Link to={logoDestination} className="font-bold">
          Vacantia
        </Link>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Cambiar tema">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger className="outline-none">
                <Avatar size="sm">
                  <AvatarFallback>{userEmail?.[0]?.toUpperCase() ?? "?"}</AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64">
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="truncate font-normal text-muted-foreground">
                    {userEmail}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {roles.includes("Postulante") && (
                    <DropdownMenuItem render={<Link to="/perfil" />}>Mi perfil</DropdownMenuItem>
                  )}
                  <DropdownMenuItem variant="destructive" onClick={handleLogout}>
                    Cerrar sesión
                  </DropdownMenuItem>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link to="/login" className="text-sm text-muted-foreground hover:text-foreground">
              Ingresar
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
