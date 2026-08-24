import type { Puesto } from "@/lib/api";

export const MODALIDAD_LABEL: Record<Puesto["modalidad"], string> = {
  presencial: "Presencial",
  remoto: "Remoto",
  hibrido: "Híbrido",
};
