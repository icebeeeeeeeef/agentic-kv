import json
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "patches" / "manifest.json"


class PatchProvenanceContractTest(unittest.TestCase):
    def test_planned_series_are_pinned_and_not_mistaken_for_patches(self) -> None:
        """A PLANNED series reserves a verified upstream boundary, not a patch claim."""
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

        self.assertEqual(manifest["schema_version"], 1)
        self.assertFalse(manifest["vendor_upstream"])
        self.assertEqual(
            manifest["materialized_patch_entry_fields"], ["path", "sha256"]
        )
        self.assertEqual(
            [series["id"] for series in manifest["series"]],
            [
                "mooncake-d1-observation",
                "sglang-trace-correlation",
                "sglang-l3-admission",
            ],
        )

        expected_commits = {
            "mooncake-d1-observation": "6041a609a8c3af35e778f70db344f145c2914980",
            "sglang-trace-correlation": "b058dc910619c9d4bce9e9e24117104ffc491fa6",
            "sglang-l3-admission": "b058dc910619c9d4bce9e9e24117104ffc491fa6",
        }
        for ordinal, series in enumerate(manifest["series"], start=1):
            with self.subTest(series=series["id"]):
                self.assertEqual(series["state"], "PLANNED")
                self.assertEqual(series["execution_order"], ordinal)
                self.assertEqual(series["upstream"]["commit"], expected_commits[series["id"]])
                self.assertEqual(series["patches"], [])
                patch_directory = REPOSITORY_ROOT / series["patch_directory"]
                self.assertTrue(patch_directory.is_dir())
                self.assertEqual(list(patch_directory.glob("*.patch")), [])
                self.assertIn("git -C <checkout> am", series["apply_command"])
                self.assertIn("git -C <checkout> am --abort", series["abort_command"])


if __name__ == "__main__":
    unittest.main()
