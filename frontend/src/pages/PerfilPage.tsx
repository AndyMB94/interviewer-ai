import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/context/AuthContext";
import {
  fetchDepartamentos,
  fetchDistritos,
  fetchPerfil,
  fetchProvincias,
  updatePerfil,
  type ApplicantProfile,
  type Distrito,
} from "@/lib/api";

const TIPO_DOCUMENTO_LABEL: Record<ApplicantProfile["tipo_documento"], string> = {
  "": "Sin especificar",
  dni: "DNI",
  ce: "Carné de Extranjería",
  pasaporte: "Pasaporte",
};

const SEXO_LABEL: Record<ApplicantProfile["sexo"], string> = {
  "": "Sin especificar",
  m: "Masculino",
  f: "Femenino",
};

export function PerfilPage() {
  const { accessToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [tipoDocumento, setTipoDocumento] = useState<ApplicantProfile["tipo_documento"]>("");
  const [numeroDocumento, setNumeroDocumento] = useState("");
  const [nacionalidad, setNacionalidad] = useState("");
  const [fechaNacimiento, setFechaNacimiento] = useState("");
  const [sexo, setSexo] = useState<ApplicantProfile["sexo"]>("");
  const [telefono, setTelefono] = useState("");
  const [departamento, setDepartamento] = useState("");
  const [provincia, setProvincia] = useState("");
  const [distrito, setDistrito] = useState("");
  const [ubigeoCodigo, setUbigeoCodigo] = useState("");

  const [departamentos, setDepartamentos] = useState<string[]>([]);
  const [provincias, setProvincias] = useState<string[]>([]);
  const [distritos, setDistritos] = useState<Distrito[]>([]);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!accessToken) return;
    fetchPerfil(accessToken)
      .then((perfil) => {
        setTipoDocumento(perfil.tipo_documento);
        setNumeroDocumento(perfil.numero_documento);
        setNacionalidad(perfil.nacionalidad);
        setFechaNacimiento(perfil.fecha_nacimiento ?? "");
        setSexo(perfil.sexo);
        setTelefono(perfil.telefono);
        setDepartamento(perfil.departamento);
        setProvincia(perfil.provincia);
        setDistrito(perfil.distrito);
        setUbigeoCodigo(perfil.ubigeo_codigo);
      })
      .catch((error: Error) => setLoadError(error.message))
      .finally(() => setLoading(false));
  }, [accessToken]);

  useEffect(() => {
    fetchDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]));
  }, []);

  useEffect(() => {
    if (!departamento) return;
    fetchProvincias(departamento)
      .then(setProvincias)
      .catch(() => setProvincias([]));
  }, [departamento]);

  useEffect(() => {
    if (!departamento || !provincia) return;
    fetchDistritos(departamento, provincia)
      .then(setDistritos)
      .catch(() => setDistritos([]));
  }, [departamento, provincia]);

  const handleDepartamentoChange = (value: string | null) => {
    setDepartamento(value ?? "");
    setProvincia("");
    setDistrito("");
    setUbigeoCodigo("");
  };

  const handleProvinciaChange = (value: string | null) => {
    setProvincia(value ?? "");
    setDistrito("");
    setUbigeoCodigo("");
  };

  const handleDistritoChange = (value: string | null) => {
    setDistrito(value ?? "");
    setUbigeoCodigo(distritos.find((d) => d.distrito === value)?.ubigeo ?? "");
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!accessToken) return;

    setSubmitting(true);
    setSubmitError(null);
    setSaved(false);
    try {
      await updatePerfil(accessToken, {
        tipo_documento: tipoDocumento,
        numero_documento: numeroDocumento,
        nacionalidad,
        fecha_nacimiento: fechaNacimiento || null,
        sexo,
        telefono,
        departamento,
        provincia,
        distrito,
        ubigeo_codigo: ubigeoCodigo,
      });
      setSaved(true);
    } catch (error) {
      setSubmitError((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-2xl space-y-4 p-4 pt-8">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (loadError) {
    return (
      <p className="mx-auto w-full max-w-2xl p-4 pt-8 text-center text-destructive">{loadError}</p>
    );
  }

  return (
    <div className="mx-auto w-full max-w-2xl p-4 pt-8">
      <Card>
        <CardHeader>
          <CardTitle>Mi perfil</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <Label>Tipo de documento</Label>
              <Select
                value={tipoDocumento || "none"}
                onValueChange={(value) =>
                  setTipoDocumento((value === "none" ? "" : value) as ApplicantProfile["tipo_documento"])
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue>
                    {() => TIPO_DOCUMENTO_LABEL[tipoDocumento]}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="none">Sin especificar</SelectItem>
                    <SelectItem value="dni">DNI</SelectItem>
                    <SelectItem value="ce">Carné de Extranjería</SelectItem>
                    <SelectItem value="pasaporte">Pasaporte</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="numero-documento">Número de documento</Label>
              <Input
                id="numero-documento"
                value={numeroDocumento}
                onChange={(event) => setNumeroDocumento(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="nacionalidad">Nacionalidad</Label>
              <Input
                id="nacionalidad"
                value={nacionalidad}
                onChange={(event) => setNacionalidad(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="fecha-nacimiento">Fecha de nacimiento</Label>
              <Input
                id="fecha-nacimiento"
                type="date"
                value={fechaNacimiento}
                onChange={(event) => setFechaNacimiento(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Sexo</Label>
              <Select
                value={sexo || "none"}
                onValueChange={(value) =>
                  setSexo((value === "none" ? "" : value) as ApplicantProfile["sexo"])
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue>{() => SEXO_LABEL[sexo]}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="none">Sin especificar</SelectItem>
                    <SelectItem value="m">Masculino</SelectItem>
                    <SelectItem value="f">Femenino</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="telefono">Teléfono</Label>
              <Input
                id="telefono"
                value={telefono}
                onChange={(event) => setTelefono(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Departamento</Label>
              <Select value={departamento || "none"} onValueChange={handleDepartamentoChange}>
                <SelectTrigger className="w-full">
                  <SelectValue>{() => departamento || "Sin especificar"}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {departamentos.map((nombre) => (
                      <SelectItem key={nombre} value={nombre}>
                        {nombre}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Provincia</Label>
              <Select
                value={provincia || "none"}
                onValueChange={handleProvinciaChange}
                disabled={!departamento}
              >
                <SelectTrigger className="w-full">
                  <SelectValue>{() => provincia || "Sin especificar"}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {provincias.map((nombre) => (
                      <SelectItem key={nombre} value={nombre}>
                        {nombre}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label>Distrito</Label>
              <Select
                value={distrito || "none"}
                onValueChange={handleDistritoChange}
                disabled={!provincia}
              >
                <SelectTrigger className="w-full">
                  <SelectValue>{() => distrito || "Sin especificar"}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {distritos.map((d) => (
                      <SelectItem key={d.distrito} value={d.distrito}>
                        {d.distrito}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            {submitError && <p className="text-sm text-destructive">{submitError}</p>}
            {saved && <p className="text-sm text-muted-foreground">Perfil guardado.</p>}

            <Button type="submit" disabled={submitting}>
              {submitting && <Spinner data-icon="inline-start" />}
              {submitting ? "Guardando..." : "Guardar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
