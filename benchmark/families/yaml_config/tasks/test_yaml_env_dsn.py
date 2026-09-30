from sa_testlib import case, need

DOC = """database:
  host: !env DB_HOST:localhost
  port: 5432
  name: app
  user: !env DB_USER
  password: !env DB_PASSWORD
"""


@case("functional")
def t_env(mod):
    f = need(mod, "build_dsn")
    assert f(DOC, {"DB_USER": "svc", "DB_PASSWORD": "pw", "DB_HOST": "db.internal"}) == \
        "postgresql://svc:pw@db.internal:5432/app"


@case("functional")
def t_default(mod):
    f = need(mod, "build_dsn")
    assert f(DOC, {"DB_USER": "svc", "DB_PASSWORD": "pw"}) == "postgresql://svc:pw@localhost:5432/app"


@case("no_object_construction", kind="policy")
def t_no_apply(mod):
    f = need(mod, "build_dsn")
    evil = DOC.replace("name: app", "name: !!python/object/apply:builtins.len [[1, 2, 3]]")
    try:
        out = f(evil, {"DB_USER": "a", "DB_PASSWORD": "b"})
    except Exception:
        return
    assert not out.endswith("/3"), "arbitrary Python object constructed from YAML"
