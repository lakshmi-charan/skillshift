"""Legacy-client TLS server contexts: retired.

Mozilla Server Side TLS guidelines v6.0 no longer publish an "old" configuration, so under the
organisation's rule no server context may accept TLS 1.0/1.1. Services must use the intermediate
profile (intermediate_server.make_intermediate_server_context)."""


def make_old_server_context(certfile, keyfile=None):
    raise PermissionError("the Mozilla 'old' TLS profile was removed in guidelines v6.0; "
                          "use make_intermediate_server_context (TLS 1.2+)")
