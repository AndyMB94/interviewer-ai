import { createBrowserRouter } from "react-router";
import { InterviewPage } from "./pages/InterviewPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <InterviewPage />,
  },
]);
