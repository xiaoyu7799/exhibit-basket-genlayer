# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

API = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
IMAGE = "https://images.metmuseum.org/"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def pack(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def inspect_object(identifier):
    source = API + str(identifier)
    response = gl.nondet.web.get(source)
    if response.status == 404:
        return {"id": identifier, "reason": "NOT_FOUND", "image": "", "source": source}
    require(response.status == 200 and len(response.body) <= 250000, "CATALOG_UNAVAILABLE")
    item = json.loads(response.body.decode("utf-8"))
    require(item.get("objectID") == identifier, "CATALOG_ID_MISMATCH")
    rights = item.get("isPublicDomain")
    image = item.get("primaryImage")
    require(type(rights) is bool, "INVALID_CATALOG_FIELDS")
    has_official_image = type(image) is str and image.startswith(IMAGE) and len(image) > len(IMAGE)
    reason = "NO_OFFICIAL_IMAGE" if not has_official_image else ("READY" if rights else "NOT_PUBLIC_DOMAIN")
    return {"id": identifier, "reason": reason, "image": image if reason == "READY" else "", "source": source}


def assess(slots):
    def fetch():
        return [[inspect_object(identifier) for identifier in slot] for slot in slots]

    def validate(proposal):
        if not isinstance(proposal, gl.vm.Return):
            return False
        try:
            return pack(proposal.calldata) == pack(fetch())
        except Exception:
            return False

    return gl.vm.run_nondet_unsafe(fetch, validate)


def choose(evidence):
    return [next((item for item in slot if item["reason"] == "READY"), None) for slot in evidence]


class ExhibitBasket(gl.Contract):
    editions: TreeMap[u256, str]
    count: u256

    def __init__(self):
        self.count = u256(0)

    @gl.public.write
    def propose(self, label: str, ranked_slots_json: str) -> u256:
        require(1 <= len(label.strip()) <= 100 and len(label) <= 100, "BAD_LABEL")
        require(len(ranked_slots_json) <= 512, "BAD_INPUT")
        slots = json.loads(ranked_slots_json)
        require(type(slots) is list and 1 <= len(slots) <= 3, "BAD_SLOTS")
        seen = set()
        for slot in slots:
            require(type(slot) is list and 1 <= len(slot) <= 3, "BAD_SLOT")
            for item in slot:
                require(type(item) is int and 0 < item < 10000000 and item not in seen, "BAD_OR_DUPLICATE_ID")
                seen.add(item)
        key = self.count
        self.editions[key] = pack({"editor": str(gl.message.sender_address).lower(), "label": label.strip(),
                                   "slots": slots, "state": "PROPOSED"})
        self.count = u256(int(key) + 1)
        return key

    @gl.public.write
    def resolve(self, edition: u256) -> None:
        require(int(edition) < int(self.count), "UNKNOWN_EDITION")
        record = json.loads(self.editions[edition])
        require(record["state"] == "PROPOSED", "EDITION_CLOSED")
        evidence = assess(record["slots"])
        selected = choose(evidence)
        record["evidence"] = evidence
        record["state"] = "PUBLISHED" if all(item is not None for item in selected) else "BLOCKED"
        record["manifest"] = selected if record["state"] == "PUBLISHED" else []
        self.editions[edition] = pack(record)

    @gl.public.view
    def get_edition(self, edition: u256) -> str:
        require(int(edition) < int(self.count), "UNKNOWN_EDITION")
        return self.editions[edition]

    @gl.public.view
    def snapshot(self) -> str:
        return pack({"count": int(self.count)})
