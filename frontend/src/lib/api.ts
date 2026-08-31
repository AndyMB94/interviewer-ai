const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Categoria {
  id: number;
  nombre: string;
}

export interface Puesto {
  id: number;
  titulo: string;
  descripcion: string;
  funciones: string;
  requisitos: string;
  requisitos_deseables: string;
  modalidad: "presencial" | "remoto" | "hibrido";
  vacantes: number;
  categoria: number | null;
  categoria_nombre: string | null;
  estado: "abierto" | "cerrado";
  limite_postulaciones: number;
  acepta_postulaciones: boolean;
  postulaciones_count: number;
  preseleccionados: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export async function fetchCategorias(): Promise<Categoria[]> {
  const response = await fetch(`${API_URL}/api/categorias/`);
  if (!response.ok) {
    throw new Error("No se pudieron cargar las categorías.");
  }
  return response.json();
}

export async function fetchPuestosAbiertos(
  categoriaId?: number,
  page = 1,
): Promise<PaginatedResponse<Puesto>> {
  const url = new URL(`${API_URL}/api/puestos/`);
  if (categoriaId) {
    url.searchParams.set("categoria", String(categoriaId));
  }
  url.searchParams.set("page", String(page));
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("No se pudieron cargar los puestos disponibles.");
  }
  // El listado público del backend ya filtra por estado=abierto (Backend 9.11.2) — no hace falta
  // repetir el filtro acá.
  return response.json();
}

export async function fetchPuesto(id: number): Promise<Puesto> {
  const response = await fetch(`${API_URL}/api/puestos/${id}/`);
  if (!response.ok) {
    throw new Error("No se pudo cargar el puesto.");
  }
  return response.json();
}

export async function fetchMisPuestos(
  token: string,
  options: { page?: number; search?: string; estado?: Puesto["estado"] } = {},
): Promise<PaginatedResponse<Puesto>> {
  const { page = 1, search, estado } = options;
  const url = new URL(`${API_URL}/api/puestos/`);
  url.searchParams.set("mias", "true");
  url.searchParams.set("page", String(page));
  if (search) url.searchParams.set("search", search);
  if (estado) url.searchParams.set("estado", estado);
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudieron cargar tus puestos.");
  }
  return response.json();
}

export interface PuestoFormPayload {
  titulo: string;
  descripcion: string;
  funciones: string;
  requisitos: string;
  requisitos_deseables: string;
  modalidad: Puesto["modalidad"];
  vacantes: number;
  categoria: number | null;
  limite_postulaciones: number;
}

export async function createPuesto(token: string, payload: PuestoFormPayload): Promise<Puesto> {
  const response = await fetch(`${API_URL}/api/puestos/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("No se pudo crear el puesto.");
  }
  return response.json();
}

export async function updatePuesto(
  token: string,
  id: number,
  payload: Partial<PuestoFormPayload> & { estado?: Puesto["estado"] },
): Promise<Puesto> {
  const response = await fetch(`${API_URL}/api/puestos/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("No se pudo actualizar el puesto.");
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
  interview_id: number | null;
}

export async function fetchMisPostulaciones(
  token: string,
  options: { page?: number; search?: string; estado?: Postulacion["estado"] } = {},
): Promise<PaginatedResponse<Postulacion>> {
  const { page = 1, search, estado } = options;
  const url = new URL(`${API_URL}/api/postulaciones/`);
  url.searchParams.set("page", String(page));
  if (search) url.searchParams.set("search", search);
  if (estado) url.searchParams.set("estado", estado);
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudieron cargar las postulaciones.");
  }
  return response.json();
}

export interface InterviewQuestion {
  question: string;
  created_at: string;
  answer: string | null;
  answered_at: string | null;
}

export type InterviewDecision = "pendiente" | "avanza" | "no_avanza";

export interface InterviewDetail {
  id: number;
  status: "in_progress" | "finished";
  decision: InterviewDecision;
  created_at: string;
  postulacion: {
    nombre: string;
    puesto_titulo: string;
    estado: "pendiente" | "aprobado" | "rechazado";
    resultado_filtro: string;
  };
  questions: InterviewQuestion[];
}

export async function fetchInterviewDetail(token: string, interviewId: number): Promise<InterviewDetail> {
  const response = await fetch(`${API_URL}/api/interviews/${interviewId}/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudo cargar el detalle de la entrevista.");
  }
  return response.json();
}

export async function updateInterviewDecision(
  token: string,
  interviewId: number,
  decision: InterviewDecision,
): Promise<void> {
  const response = await fetch(`${API_URL}/api/interviews/${interviewId}/decision/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ decision }),
  });
  if (!response.ok) {
    throw new Error("No se pudo actualizar la decisión.");
  }
}

export interface MiPostulacion {
  id: number;
  nombre: string;
  puesto: { id: number; titulo: string };
}

export async function fetchMisPostulacionesPendientes(token: string): Promise<MiPostulacion[]> {
  const response = await fetch(`${API_URL}/api/postulaciones/mia/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("No se pudo cargar la información de la postulación.");
  }
  return response.json();
}

export interface MiPostulacionCompleta {
  id: number;
  puesto: { id: number; titulo: string };
  estado: "pendiente" | "aprobado" | "rechazado";
  created_at: string;
  fecha_limite_entrevista: string | null;
  entrevista_vencida: boolean;
  tiene_entrevista: boolean;
  entrevista_finalizada: boolean;
}

// Fase 12: a diferencia de fetchMisPostulacionesPendientes (solo aprobadas y sin entrevistar,
// para el selector de puesto), esto trae TODAS las postulaciones para el panel "mis postulaciones".
export async function fetchMisPostulacionesTodas(token: string): Promise<MiPostulacionCompleta[]> {
  const response = await fetch(`${API_URL}/api/postulaciones/mias/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("No se pudo cargar el estado de sus postulaciones.");
  }
  return response.json();
}

export interface InterviewEnCurso {
  interview_id: number;
  postulacion_id: number | null;
  puesto_titulo: string | null;
  created_at: string;
  questions: InterviewQuestion[];
}

// Fase 10.4/10.5: si el candidato cerró el navegador a medio camino, esto detecta la entrevista
// sin terminar para poder retomarla -- null cuando no tiene ninguna (204 No Content del backend).
export async function fetchInterviewEnCurso(token: string): Promise<InterviewEnCurso | null> {
  const response = await fetch(`${API_URL}/api/interviews/en-curso/`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 204) return null;
  if (!response.ok) {
    throw new Error("No se pudo verificar si tiene una entrevista en curso.");
  }
  return response.json();
}

export interface ApplicantProfile {
  tipo_documento: "" | "dni" | "ce" | "pasaporte";
  numero_documento: string;
  nacionalidad: string;
  fecha_nacimiento: string | null;
  sexo: "" | "m" | "f";
  telefono: string;
  ubigeo_codigo: string;
  departamento: string;
  provincia: string;
  distrito: string;
}

export async function fetchPerfil(token: string): Promise<ApplicantProfile> {
  const response = await fetch(`${API_URL}/api/auth/perfil/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error("No se pudo cargar tu perfil.");
  }
  return response.json();
}

export async function updatePerfil(
  token: string,
  payload: Partial<ApplicantProfile>,
): Promise<ApplicantProfile> {
  const response = await fetch(`${API_URL}/api/auth/perfil/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("No se pudo guardar tu perfil.");
  }
  return response.json();
}

export async function fetchDepartamentos(): Promise<string[]> {
  const response = await fetch(`${API_URL}/api/auth/ubigeo/departamentos/`);
  if (!response.ok) {
    throw new Error("No se pudo cargar la lista de departamentos.");
  }
  return response.json();
}

export async function fetchProvincias(departamento: string): Promise<string[]> {
  const url = new URL(`${API_URL}/api/auth/ubigeo/provincias/`);
  url.searchParams.set("departamento", departamento);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("No se pudo cargar la lista de provincias.");
  }
  return response.json();
}

export interface Distrito {
  distrito: string;
  ubigeo: string;
}

export async function fetchDistritos(departamento: string, provincia: string): Promise<Distrito[]> {
  const url = new URL(`${API_URL}/api/auth/ubigeo/distritos/`);
  url.searchParams.set("departamento", departamento);
  url.searchParams.set("provincia", provincia);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("No se pudo cargar la lista de distritos.");
  }
  return response.json();
}
