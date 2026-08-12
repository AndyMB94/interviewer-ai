import { Outlet } from "react-router";
import { Navbar } from "@/components/Navbar";
import { TooltipProvider } from "@/components/ui/tooltip";

export function RootLayout() {
  return (
    <TooltipProvider>
      <div className="min-h-screen">
        <Navbar />
        <Outlet />
      </div>
    </TooltipProvider>
  );
}
