"""Small SDK stand-in for isolated tests. It supplies no network evidence."""
import importlib.util
import sys
import types


class Map(dict):
    @classmethod
    def __class_getitem__(cls, item):
        return cls


class Return:
    def __init__(self, value):
        self.calldata = value


class Host:
    Contract = object

    def __init__(self):
        self.message = types.SimpleNamespace(sender_address="0x" + "a" * 40)
        self.public = types.SimpleNamespace(write=lambda f: f, view=lambda f: f)
        self.vm = types.SimpleNamespace(Return=Return, run_nondet_unsafe=self.run)
        self.nondet = types.SimpleNamespace(web=types.SimpleNamespace(get=self.get))
        self.responses = {}
        self.proposed = None

    def get(self, url):
        status, body = self.responses[url]
        return types.SimpleNamespace(status=status, body=body)

    def run(self, fetch, validate):
        candidate = fetch() if self.proposed is None else self.proposed
        if not validate(Return(candidate)):
            raise ValueError("NO_CONSENSUS")
        return candidate

    def load(self, path):
        sdk = types.ModuleType("genlayer")
        sdk.gl, sdk.TreeMap, sdk.u256 = self, Map, int
        sys.modules["genlayer"] = sdk
        spec = importlib.util.spec_from_file_location("contract", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
