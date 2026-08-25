import { Outlet } from "react-router";
import { Footer } from "@/components/Footer";

export function PublicLayout() {
  return (
    <div className="flex min-w-0 flex-1 flex-col">
      <div className="relative min-w-0 flex-1">
        <Outlet />
      </div>
      <Footer />
    </div>
  );
}
