from sa_testlib import case, need


@case("split_documents")
def test_two_docs(mod):
    assert need(mod, "load_all_documents")("a: 1\n---\nb: 2\n") == [{"a": 1}, {"b": 2}]
