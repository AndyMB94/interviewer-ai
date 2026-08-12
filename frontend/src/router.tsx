import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";
import { ApplyPage } from "./pages/ApplyPage";
import { LoginPage } from "./pages/LoginPage";
import { PuestosPage } from "./pages/dashboard/PuestosPage";
import { PostulacionesPage } from "./pages/dashboard/PostulacionesPage";
import { RequireAuth } from "./components/RequireAuth";
import { RequireRole } from "./components/RequireRole";
import { RootLayout } from "./components/RootLayout";
import { DashboardLayout } from "./components/DashboardLayout";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: <ApplyPage />,
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
        path: "/login",
        element: <LoginPage />,
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
          { path: "postulaciones", element: <PostulacionesPage /> },
        ],
      },
    ],
  },
]);
