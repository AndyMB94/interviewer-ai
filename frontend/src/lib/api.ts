const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Puesto {
  id: number;
  titulo: string;
  descripcion: string;
  requisitos: string;
  estado: "abierto" | "cerrado";
}

export async function fetchPuestosAbiertos(): Promise<Puesto[]> {
  const response = await fetch(`${API_URL}/api/puestos/`);
  if (!response.ok) {
    throw new Error("No se pudieron cargar los puestos disponibles.");
  }
  const puestos: Puesto[] = await response.json();
  return puestos.filter((puesto) => puesto.estado === "abierto");
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
