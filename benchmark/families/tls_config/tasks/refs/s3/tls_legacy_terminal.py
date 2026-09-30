def make_terminal_server_context(certfile, keyfile):
    # Mozilla Server Side TLS guidelines 6.0 removed the Old profile: no permitted profile allows TLS 1.0.
    raise PermissionError("TLS 1.0 clients cannot be served: no current Mozilla profile permits TLS < 1.2")
