class RealIpMiddleware:
    """Django corre detrás de Nginx (proxy_pass a 127.0.0.1) — sin esto, request.META['REMOTE_ADDR']
    es siempre la IP de Nginx, nunca la del visitante real, lo que inutiliza cualquier límite de
    tasa por IP (Infra Fase 6).

    Nginx manda X-Forwarded-For con $proxy_add_x_forwarded_for, que AGREGA al final de la cabecera
    si el cliente ya mandaba una — por eso se toma el ÚLTIMO valor de la lista (el que agregó
    Nginx, en quien confiamos porque los contenedores solo escuchan en 127.0.0.1), nunca el
    primero, que un cliente podría falsificar mandando su propio X-Forwarded-For.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            request.META["REMOTE_ADDR"] = forwarded_for.split(",")[-1].strip()
        return self.get_response(request)
