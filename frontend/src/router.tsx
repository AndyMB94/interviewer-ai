import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";
import { ApplyPage } from "./pages/ApplyPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <InterviewPage />,
  },
  {
    path: "/postular",
    element: <ApplyPage />,
  },
]);
