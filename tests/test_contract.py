import json
import unittest
from host import Host, Map

HOST = Host()
MODULE = HOST.load("contracts/exhibit_basket.py")


class ExhibitTest(unittest.TestCase):
    def setUp(self):
        HOST.proposed = None
        HOST.responses.clear()
        self.contract = MODULE.ExhibitBasket()
        self.contract.editions = Map()
        for identifier, eligible in [(1, False), (2, True), (3, True)]:
            item = {"objectID": identifier, "isPublicDomain": eligible,
                    "primaryImage": MODULE.IMAGE + str(identifier)}
            HOST.responses[MODULE.API + str(identifier)] = (200, json.dumps(item).encode())

    def test_ranked_substitution(self):
        edition = self.contract.propose("Example", "[[1,2],[3]]")
        self.contract.resolve(edition)
        result = json.loads(self.contract.get_edition(edition))
        self.assertEqual(result["state"], "PUBLISHED")
        self.assertEqual([item["id"] for item in result["manifest"]], [2, 3])
        with self.assertRaisesRegex(ValueError, "EDITION_CLOSED"):
            self.contract.resolve(edition)

    def test_shortage_exposes_no_partial_manifest(self):
        edition = self.contract.propose("Short", "[[1],[3]]")
        self.contract.resolve(edition)
        result = json.loads(self.contract.get_edition(edition))
        self.assertEqual((result["state"], result["manifest"]), ("BLOCKED", []))

    def test_validator_rejects_forged_rights(self):
        edition = self.contract.propose("Example", "[[1]]")
        HOST.proposed = [[{"id": 1, "reason": "READY", "image": MODULE.IMAGE + "1",
                           "source": MODULE.API + "1"}]]
        with self.assertRaisesRegex(ValueError, "NO_CONSENSUS"):
            self.contract.resolve(edition)
        self.assertEqual(json.loads(self.contract.get_edition(edition))["state"], "PROPOSED")

    def test_reject_duplicate_candidate_across_slots(self):
        with self.assertRaisesRegex(ValueError, "BAD_OR_DUPLICATE_ID"):
            self.contract.propose("Duplicate", "[[1,2],[2]]")

    def test_unavailable_is_retryable(self):
        edition = self.contract.propose("Example", "[[2]]")
        HOST.responses[MODULE.API + "2"] = (503, b"")
        with self.assertRaisesRegex(ValueError, "CATALOG_UNAVAILABLE"):
            self.contract.resolve(edition)
        self.assertEqual(json.loads(self.contract.get_edition(edition))["state"], "PROPOSED")
