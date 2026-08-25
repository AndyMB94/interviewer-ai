import { LogOut, Mail, Moon, Sun, User } from "lucide-react";
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
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/hooks/useTheme";

export function NavbarActions() {
  const { isAuthenticated, userEmail, roles, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="flex items-center gap-2">
      <Tooltip>
        <TooltipTrigger
          render={
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          }
        />
        <TooltipContent>
          {theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
        </TooltipContent>
      </Tooltip>

      {isAuthenticated ? (
        <DropdownMenu>
          <DropdownMenuTrigger className="outline-none">
            <Avatar size="sm">
              <AvatarFallback>{userEmail?.[0]?.toUpperCase() ?? "?"}</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuGroup>
              <DropdownMenuLabel className="flex min-w-0 items-center gap-1.5 font-normal text-muted-foreground">
                <Mail className="h-4 w-4 shrink-0" />
                <span className="min-w-0 truncate">{userEmail}</span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {roles.includes("Postulante") && (
                <DropdownMenuItem render={<Link to="/perfil" />}>
                  <User className="h-4 w-4" />
                  Mi perfil
                </DropdownMenuItem>
              )}
              <DropdownMenuItem variant="destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
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
  );
}
