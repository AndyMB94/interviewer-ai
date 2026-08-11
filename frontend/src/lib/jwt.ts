export function decodeJwtRoles(token: string): string[] {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.groups ?? [];
  } catch {
    return [];
  }
}
