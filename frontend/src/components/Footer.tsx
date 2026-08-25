import { Code2 } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-4xl flex-col items-center gap-2 p-4 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <p>Desarrollado por Andy Mallcco.</p>
        <a
          href="https://github.com/AndyMB94/interviewer-ai"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 hover:text-foreground"
        >
          <Code2 className="h-4 w-4" />
          Ver el código en GitHub
        </a>
      </div>
    </footer>
  );
}
