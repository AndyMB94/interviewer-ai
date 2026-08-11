import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { loginRequest, logoutRequest, refreshAccessToken } from "@/lib/api";
import { decodeJwtPayload } from "@/lib/jwt";

interface AuthContextValue {
  accessToken: string | null;
  userEmail: string | null;
  roles: string[];
  isAuthenticated: boolean;
  isCheckingSession: boolean;
  login: (username: string, password: string) => Promise<string[]>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  const [isCheckingSession, setIsCheckingSession] = useState(true);

  // Silent refresh (Frontend Fase P.7): al cargar la app, intenta restaurar la sesión con la
  // cookie httpOnly del refresh token, sin pedir credenciales de nuevo. El access token vive solo
  // en memoria (nunca localStorage) y se pierde en cada refresco de página — esto evita que haya
  // que loguearse de nuevo mientras la cookie (7 días) siga siendo válida.
  useEffect(() => {
    refreshAccessToken()
      .then((token) => {
        const { roles: decodedRoles, email } = decodeJwtPayload(token);
        setAccessToken(token);
        setUserEmail(email);
        setRoles(decodedRoles);
      })
      .catch(() => {
        // sin cookie válida (nunca inició sesión, o ya venció) — se queda como no logueado
      })
      .finally(() => setIsCheckingSession(false));
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const token = await loginRequest(username, password);
    const { roles: decodedRoles, email } = decodeJwtPayload(token);
    setAccessToken(token);
    setUserEmail(email ?? username);
    setRoles(decodedRoles);
    return decodedRoles;
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    setAccessToken(null);
    setUserEmail(null);
    setRoles([]);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        userEmail,
        roles,
        isAuthenticated: !!accessToken,
        isCheckingSession,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }
  return context;
}
