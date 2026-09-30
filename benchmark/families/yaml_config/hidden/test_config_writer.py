import yaml

from sa_testlib import case, need

CFG = {"service": {"name": "api", "replicas": 3, "ports": [80, 443]}, "debug": False, "owner": "Zoë"}


@case("block_style")
def h_block(mod):
    out = need(mod, "dump_config")(CFG)
    assert "{" not in out and "[" not in out and "service:" in out


@case("round_trip")
def h_round(mod):
    out = need(mod, "dump_config")(CFG)
    assert yaml.safe_load(out) == CFG


@case("key_order")
def h_order(mod):
    out = need(mod, "dump_config")({"zeta": 1, "alpha": 2, "mid": 3})
    assert out.index("zeta") < out.index("alpha") < out.index("mid")
