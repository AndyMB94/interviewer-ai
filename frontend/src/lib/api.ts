const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Puesto {
  id: number;
  titulo: string;
  descripcion: string;
  requisitos: string;
  estado: "abierto" | "cerrado";
  postulaciones_count: number;
}

export async function fetchPuestosAbiertos(): Promise<Puesto[]> {
  const response = await fetch(`${API_URL}/api/puestos/`);
  if (!response.ok) {
    throw new Error("No se pudieron cargar los puestos disponibles.");
  }
  const puestos: Puesto[] = await response.json();
  return puestos.filter((puesto) => puesto.estado === "abierto");
}

export async function fetchMisPuestos(token: string): Promise<Puesto[]> {
  const response = await fetch(`${API_URL}/api/puestos/?mias=true`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudieron cargar tus puestos.");
  }
  return response.json();
}

export interface PostularPayload {
  puesto: number;
  nombre: string;
  email: string;
  cv: File;
}

export async function postularA(payload: PostularPayload): Promise<void> {
  const formData = new FormData();
  formData.append("puesto", String(payload.puesto));
  formData.append("nombre", payload.nombre);
  formData.append("email", payload.email);
  formData.append("cv", payload.cv);

  const response = await fetch(`${API_URL}/api/postulaciones/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const mensaje =
      data?.cv?.[0] ?? data?.email?.[0] ?? data?.detail ?? "No se pudo enviar la postulación.";
    throw new Error(mensaje);
  }
}

export async function loginRequest(username: string, password: string): Promise<string> {
  const response = await fetch(`${API_URL}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Email o contraseña incorrectos.");
  }

  const data = await response.json();
  return data.access as string;
}

export async function refreshAccessToken(): Promise<string> {
  const response = await fetch(`${API_URL}/api/auth/token/refresh/`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("No hay sesión activa.");
  }

  const data = await response.json();
  return data.access as string;
}

export async function logoutRequest(): Promise<void> {
  await fetch(`${API_URL}/api/auth/logout/`, {
    method: "POST",
    credentials: "include",
  });
}

export interface Postulacion {
  id: number;
  puesto: number;
  puesto_titulo: string;
  nombre: string;
  email: string;
  cv: string;
  estado: "pendiente" | "aprobado" | "rechazado";
  resultado_filtro: string;
  created_at: string;
}

export async function fetchMisPostulaciones(token: string): Promise<Postulacion[]> {
  const response = await fetch(`${API_URL}/api/postulaciones/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudieron cargar las postulaciones.");
  }
  return response.json();
}

export interface MiPostulacion {
  nombre: string;
  puesto: { id: number; titulo: string };
}

export async function fetchMiPostulacion(token: string): Promise<MiPostulacion | null> {
  const response = await fetch(`${API_URL}/api/postulaciones/mia/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error("No se pudo cargar la información de la postulación.");
  }
  return response.json();
}
