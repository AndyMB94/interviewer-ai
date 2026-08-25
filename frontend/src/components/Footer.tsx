import { Code2, Mail, Phone } from "lucide-react";

function LinkedinIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-4xl flex-col items-center gap-3 p-4 text-sm text-muted-foreground sm:flex-row sm:justify-between">
        <p>Desarrollado por Andy Mallcco.</p>
        <div className="flex items-center gap-4">
          <a
            href="https://www.linkedin.com/in/andy-ayrton-mallcco-bohorquez/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            title="LinkedIn"
            className="transition-colors hover:text-foreground"
          >
            <LinkedinIcon />
          </a>
          <a
            href="mailto:andy.mallcco@tecsup.edu.pe"
            aria-label="Email"
            title="andy.mallcco@tecsup.edu.pe"
            className="transition-colors hover:text-foreground"
          >
            <Mail className="h-4 w-4" />
          </a>
          <a
            href="tel:+51927939655"
            aria-label="Teléfono"
            title="+51 927 939 655"
            className="transition-colors hover:text-foreground"
          >
            <Phone className="h-4 w-4" />
          </a>
          <a
            href="https://github.com/AndyMB94/interviewer-ai"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Ver el código en GitHub"
            title="Ver el código en GitHub"
            className="transition-colors hover:text-foreground"
          >
            <Code2 className="h-4 w-4" />
          </a>
        </div>
      </div>
    </footer>
  );
}
