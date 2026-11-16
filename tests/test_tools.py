"""Regression checks using synthetic evidence and temporary workspaces."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract_figures = load_script("extract_figures")
validate_report = load_script("validate_report")


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def run_script(self, name: str, *arguments: object):
        return subprocess.run(
            [
                sys.executable,
                "-B",
                "-X",
                "utf8",
                str(SCRIPTS / f"{name}.py"),
                *map(str, arguments),
            ],
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

    def write_json(self, path: Path, value: object):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def report_fixture(self, figure_count: int = 0):
        report = self.root / "report.md"
        bodies = {
            name: f"Verified explanation. (Evidence: Sec. {number})"
            for number, name in enumerate(
                ("What", "Why", "How", "Experiment", "Question"), start=1
            )
        }
        entries = []
        for number in range(1, figure_count + 1):
            image = f"extracted/figures/source-Figure{number}-1.png"
            image_path = self.root / image
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(b"synthetic image-existence fixture")
            entries.append(
                {
                    "figType": "Figure",
                    "name": str(number),
                    "image": image,
                    "status": "extracted",
                }
            )
            bodies["How"] += f"\n\n![Figure {number}]({image})"
        report.write_text(
            "# Synthetic Paper\n\n"
            + "\n\n".join(
                f"## {number}. {name}\n\n{body}"
                for number, (name, body) in enumerate(bodies.items(), start=1)
            ),
            encoding="utf-8",
        )
        manifest = {"source": "pdffigures2", "items": entries}
        analysis = {
            "complete": True,
            "items": [
                {**item, "status": "analyzed", "readable": True, "section": "how"}
                for item in entries
            ],
        }
        plan = {
            "complete": True,
            "items": [
                {
                    "id": f"Figure {item['name']}",
                    "image": item["image"],
                    "section": "how",
                    "include": True,
                    "covers": [f"mechanism-{item['name']}"],
                    "reason": "An independent mechanism.",
                    "duplicate_of": "",
                }
                for item in entries
            ],
            "claims": [
                {
                    "claim": "A synthetic paper claim.",
                    "evidence": ["Sec. 4"],
                    "visuals": [],
                    "presentation": "text",
                    "reason": "Text is sufficient for this fixture.",
                }
            ],
        }
        return report, manifest, analysis, plan

    def save_visuals(self, manifest: dict, analysis: dict, plan: dict):
        for filename, value in (
            ("figure_manifest.json", manifest),
            ("visual_analysis.json", analysis),
            ("visual_plan.json", plan),
        ):
            self.write_json(self.root / "extracted" / filename, value)

    def test_scaffold_creates_workspace_and_preserves_existing_work(self):
        source = self.root / "fake.pdf"
        source.write_bytes(b"%PDF synthetic copy-only fixture")
        output = self.root / "reports"
        arguments = (source, "--title", "Example Paper", "--out-root", output)
        created = self.run_script("make_report_scaffold", *arguments)
        self.assertEqual(created.returncode, 0, created.stderr)
        workspace = output / "example-paper"
        copied_source = workspace / "source.pdf"
        report = workspace / "report.md"
        self.assertEqual(copied_source.read_bytes(), source.read_bytes())
        self.assertIn("Example Paper", report.read_text(encoding="utf-8"))
        self.assertTrue((workspace / "extracted" / "figures").is_dir())
        copied_source.write_bytes(b"An existing annotated source")
        report.write_text("Existing user report", encoding="utf-8")
        refused = self.run_script("make_report_scaffold", *arguments)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(copied_source.read_bytes(), b"An existing annotated source")
        self.assertEqual(report.read_text(encoding="utf-8"), "Existing user report")

    def test_index_generation_preserves_annotated_index(self):
        extracted = self.root / "extracted"
        self.write_json(
            extracted / "sections.json",
            {
                "pdf": "source.pdf",
                "pages": [
                    {
                        "page": 3,
                        "paragraphs": [{"id": "P0007", "text": "3 Method"}],
                    }
                ],
            },
        )
        target = self.root / "paper_index.json"
        arguments = ("--extracted", extracted, "--out", target)
        created = self.run_script("build_paper_index", *arguments)
        self.assertEqual(created.returncode, 0, created.stderr)
        index = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(index["section_candidates"][0]["paragraph_id"], "P0007")
        index["notes"].append("A human reading note.")
        self.write_json(target, index)
        original = target.read_bytes()
        refused = self.run_script("build_paper_index", *arguments)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(target.read_bytes(), original)

    def test_normalization_retains_metadata_and_converts_page_number(self):
        figures = self.root / "extracted" / "figures"
        figures.mkdir(parents=True)
        image = figures / "source-Figure1-1.png"
        image.write_bytes(b"synthetic image")
        original = {
            "figType": "Figure",
            "name": "1",
            "page": 0,
            "renderURL": str(image),
            "custom": {"preserve": True},
        }
        raw = copy.deepcopy(original)
        item = extract_figures.normalize_items([raw], figures, self.root)[0]
        self.assertEqual(item["status"], "extracted")
        self.assertEqual(item["pdf_page"], 1)
        self.assertEqual(item["image"], "extracted/figures/source-Figure1-1.png")
        self.assertEqual(item["custom"], original["custom"])
        self.assertEqual(raw, original)

    def test_normalization_keeps_regionless_missing_and_outside_images_unavailable(self):
        figures = self.root / "extracted" / "figures"
        figures.mkdir(parents=True)
        outside = self.root / "outside.png"
        outside.write_bytes(b"outside extraction directory")
        raw = {
            "figures": [
                {"figType": "Figure", "name": "1", "page": 2},
                {
                    "figType": "Figure",
                    "name": "2",
                    "page": -1,
                    "renderURL": str(figures / "missing.png"),
                },
                {
                    "figType": "Figure",
                    "name": "3",
                    "page": True,
                    "renderURL": str(outside),
                },
            ],
            "regionless-captions": [
                {"figType": "Table", "name": "1", "page": 4, "text": "Caption only"}
            ],
        }
        items = extract_figures.normalize_items(raw, figures, self.root)
        self.assertEqual(len(items), 4)
        for item in items:
            self.assertEqual(item["status"], "unavailable")
            self.assertEqual(item["image"], "")
            self.assertTrue(item["unavailable_reason"])
        self.assertEqual([item["pdf_page"] for item in items], [3, None, None, 5])
        self.assertEqual(items[-1]["caption"], "Caption only")

    def test_full_report_without_figures_requires_complete_visual_evidence(self):
        report, manifest, analysis, plan = self.report_fixture()
        self.assertTrue(validate_report.validate_report(report))
        self.assertNotEqual(self.run_script("validate_report", report).returncode, 0)
        self.save_visuals(manifest, analysis, plan)
        self.assertEqual(validate_report.validate_report(report), [])
        self.assertEqual(self.run_script("validate_report", report).returncode, 0)

    def test_validator_rejects_image_identity_swaps(self):
        report, manifest, analysis, plan = self.report_fixture(2)
        self.save_visuals(manifest, analysis, plan)
        self.assertEqual(validate_report.validate_report(report), [])
        for records in (analysis["items"], plan["items"]):
            records[0]["image"], records[1]["image"] = (
                records[1]["image"],
                records[0]["image"],
            )
        self.save_visuals(manifest, analysis, plan)
        problems = validate_report.validate_report(report)
        self.assertTrue(any("manifest image path" in problem for problem in problems))

    def test_validator_rejects_duplicate_manifest_and_analysis_ids(self):
        report, manifest, analysis, plan = self.report_fixture(1)
        for target in ("manifest", "analysis"):
            with self.subTest(target=target):
                current_manifest = copy.deepcopy(manifest)
                current_analysis = copy.deepcopy(analysis)
                records = (
                    current_manifest if target == "manifest" else current_analysis
                )["items"]
                records.append(copy.deepcopy(records[0]))
                self.save_visuals(current_manifest, current_analysis, plan)
                problems = validate_report.validate_report(report)
                self.assertTrue(any("duplicate" in problem.lower() for problem in problems))

    def test_validator_rejects_unreadable_image_marked_analyzed(self):
        report, manifest, analysis, plan = self.report_fixture(1)
        analysis["items"][0]["readable"] = False
        self.save_visuals(manifest, analysis, plan)
        problems = validate_report.validate_report(report)
        self.assertTrue(any("unreadable" in problem.lower() for problem in problems))


if __name__ == "__main__":
    unittest.main()
