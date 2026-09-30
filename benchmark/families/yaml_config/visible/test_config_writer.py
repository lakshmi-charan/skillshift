from sa_testlib import case, need


@case("block_style")
def test_block(mod):
    out = need(mod, "dump_config")({"db": {"host": "h", "port": 1}})
    assert "{" not in out and "db:" in out
