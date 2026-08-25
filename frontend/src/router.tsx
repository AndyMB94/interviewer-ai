import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";
import { ApplyPage } from "./pages/ApplyPage";
import { PuestoDetailPage } from "./pages/PuestoDetailPage";
import { LoginPage } from "./pages/LoginPage";
import { PerfilPage } from "./pages/PerfilPage";
import { PuestosPage } from "./pages/dashboard/PuestosPage";
import { PuestoFormPage } from "./pages/dashboard/PuestoFormPage";
import { PostulacionesPage } from "./pages/dashboard/PostulacionesPage";
import { InterviewDetailPage } from "./pages/dashboard/InterviewDetailPage";
import { RequireAuth } from "./components/RequireAuth";
import { RequireRole } from "./components/RequireRole";
import { RootLayout } from "./components/RootLayout";
import { PublicLayout } from "./components/PublicLayout";
import { DashboardLayout } from "./components/DashboardLayout";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        element: <PublicLayout />,
        children: [
          {
            path: "/",
            element: <ApplyPage />,
          },
          {
            path: "/puestos/:id",
            element: <PuestoDetailPage />,
          },
          {
            path: "/login",
            element: <LoginPage />,
          },
        ],
      },
      {
        path: "/entrevista",
        element: (
          <RequireAuth>
            <InterviewPage />
          </RequireAuth>
        ),
      },
      {
        path: "/perfil",
        element: (
          <RequireRole role="Postulante">
            <PerfilPage />
          </RequireRole>
        ),
      },
      {
        path: "/dashboard",
        element: (
          <RequireRole role="Reclutador">
            <DashboardLayout />
          </RequireRole>
        ),
        children: [
          { index: true, element: <PuestosPage /> },
          { path: "puestos/nuevo", element: <PuestoFormPage /> },
          { path: "puestos/:id/editar", element: <PuestoFormPage /> },
          { path: "postulaciones", element: <PostulacionesPage /> },
          { path: "entrevistas/:id", element: <InterviewDetailPage /> },
        ],
      },
    ],
  },
]);
