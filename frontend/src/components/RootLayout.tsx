import { Outlet } from "react-router";
import { Navbar } from "@/components/Navbar";

export function RootLayout() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Outlet />
    </div>
  );
}
