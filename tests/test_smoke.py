import rallytools as rt

def test_import_and_basics():
    log = rt.get_logger(__name__)
    log.info("smoke test")
    assert hasattr(rt, "__version__")
    # IO roundtrip
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "x.json"
        rt.write_json(p, {"a": 1})
        data = rt.read_json(p)
        assert data["a"] == 1
