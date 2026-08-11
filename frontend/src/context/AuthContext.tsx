import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { loginRequest, logoutRequest } from "@/lib/api";
import { decodeJwtRoles } from "@/lib/jwt";

interface AuthContextValue {
  accessToken: string | null;
  userEmail: string | null;
  roles: string[];
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<string[]>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [roles, setRoles] = useState<string[]>([]);

  const login = useCallback(async (username: string, password: string) => {
    const token = await loginRequest(username, password);
    const decodedRoles = decodeJwtRoles(token);
    setAccessToken(token);
    setUserEmail(username);
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
      value={{ accessToken, userEmail, roles, isAuthenticated: !!accessToken, login, logout }}
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
