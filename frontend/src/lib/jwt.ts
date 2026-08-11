export interface JwtPayload {
  roles: string[];
  email: string | null;
}

export function decodeJwtPayload(token: string): JwtPayload {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return { roles: payload.groups ?? [], email: payload.email ?? null };
  } catch {
    return { roles: [], email: null };
  }
}
