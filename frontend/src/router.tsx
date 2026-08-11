import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";
import { ApplyPage } from "./pages/ApplyPage";
import { LoginPage } from "./pages/LoginPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <InterviewPage />,
  },
  {
    path: "/postular",
    element: <ApplyPage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
]);
