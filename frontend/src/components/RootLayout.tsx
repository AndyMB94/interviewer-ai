import { Outlet } from "react-router";
import { Navbar } from "@/components/Navbar";
import { TooltipProvider } from "@/components/ui/tooltip";

export function RootLayout() {
  return (
    <TooltipProvider>
      <div className="flex min-h-screen flex-col">
        <Navbar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </div>
      </div>
    </TooltipProvider>
  );
}
