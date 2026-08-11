import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";
import { ApplyPage } from "./pages/ApplyPage";
import { LoginPage } from "./pages/LoginPage";
import { RequireAuth } from "./components/RequireAuth";
import { RootLayout } from "./components/RootLayout";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: (
          <RequireAuth>
            <InterviewPage />
          </RequireAuth>
        ),
      },
      {
        path: "/postular",
        element: <ApplyPage />,
      },
      {
        path: "/login",
        element: <LoginPage />,
      },
    ],
  },
]);
