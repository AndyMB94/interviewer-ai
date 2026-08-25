import { Outlet } from "react-router";
import { Footer } from "@/components/Footer";

export function PublicLayout() {
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex-1">
        <Outlet />
      </div>
      <Footer />
    </div>
  );
}
