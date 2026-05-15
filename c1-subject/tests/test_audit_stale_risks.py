import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_stale_risks import (
    audit_questions,
    validate_topic_sources,
    write_report,
)


class AuditStaleRisksTest(unittest.TestCase):
    def test_flags_known_stale_phrases_and_special_vehicle_scope(self):
        questions = [
            {
                "id": "q1",
                "question": "该违法行为记2分。",
                "answer_skill": "旧规说2分",
                "vehicle_scope": "C1-general",
                "stale_risk": "low",
            },
            {
                "id": "q2",
                "question": "驾驶A1客车应当注意什么？",
                "answer_skill": "客车专用",
                "vehicle_scope": "C1-general",
                "stale_risk": "low",
            },
            {
                "id": "q3",
                "question": "普通安全行车题",
                "answer_skill": "保持安全车距",
                "vehicle_scope": "C1-general",
                "stale_risk": "low",
            },
        ]

        findings = audit_questions(questions)

        self.assertEqual([finding["id"] for finding in findings], ["q1", "q2"])
        self.assertEqual(findings[0]["severity"], "high")
        self.assertIn("2分", findings[0]["matches"])
        self.assertEqual(findings[1]["category"], "possible_non_c1_scope")

    def test_reports_multiple_findings_for_one_question(self):
        questions = [
            {
                "id": "q1",
                "question": "A1客车违法行为一次记2分。",
                "answer_skill": "旧规引用公安部令第162号",
                "vehicle_scope": "C1-general",
                "stale_risk": "high",
            },
        ]

        findings = audit_questions(questions)

        self.assertEqual(
            [finding["category"] for finding in findings],
            ["stale_phrase", "possible_non_c1_scope"],
        )
        self.assertIn("162号", findings[0]["matches"])
        self.assertIn("A1", findings[1]["matches"])

    def test_flags_stale_phrase_variants(self):
        questions = [
            {
                "id": "q1",
                "question": "该行为扣2分。",
                "answer_skill": "",
                "vehicle_scope": "C1-general",
            },
            {
                "id": "q2",
                "question": "引用公安部令第139号。",
                "answer_skill": "",
                "vehicle_scope": "C1-general",
            },
            {
                "id": "q3",
                "question": "年满60岁需要注意换证。",
                "answer_skill": "",
                "vehicle_scope": "C1-general",
            },
        ]

        findings = audit_questions(questions)

        self.assertEqual([finding["id"] for finding in findings], ["q1", "q2", "q3"])
        self.assertIn("扣2", findings[0]["matches"])
        self.assertIn("139号", findings[1]["matches"])
        self.assertIn("60岁", findings[2]["matches"])

    def test_does_not_flag_current_point_values_as_2_point_stale_phrase(self):
        questions = [
            {
                "id": "q1",
                "question": "该违法行为一次记12分。",
                "answer_skill": "",
                "vehicle_scope": "C1-general",
            },
            {
                "id": "q2",
                "question": "该违法行为一次记6分。",
                "answer_skill": "",
                "vehicle_scope": "C1-general",
            },
        ]

        self.assertEqual(audit_questions(questions), [])

    def test_validates_topic_map_sources_exist(self):
        registry = {"sources": [{"id": "road-safety-implementation-regulation"}]}
        topic_map = {
            "road-rules": {
                "primary_source": "road-safety-implementation-regulation",
                "secondary_sources": ["road-safety-law"],
            }
        }

        self.assertEqual(
            validate_topic_sources(registry, topic_map),
            ["road-rules.secondary_sources: road-safety-law"],
        )

        registry["sources"].append({"id": "road-safety-law"})
        self.assertEqual(validate_topic_sources(registry, topic_map), [])

    def test_repository_topic_map_references_registered_sources(self):
        audit_dir = Path(__file__).parents[1] / "data" / "audits"
        registry = json.loads(
            (audit_dir / "law-source-registry.json").read_text(encoding="utf-8")
        )
        topic_map = json.loads(
            (audit_dir / "topic-map.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validate_topic_sources(registry, topic_map), [])

    def test_writes_markdown_report_with_summary(self):
        findings = [
            {
                "id": "q1",
                "severity": "high",
                "category": "stale_phrase",
                "matches": ["2分"],
                "question": "该违法行为记2分。",
                "suggested_source": "公安部令第163号",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "stale-risk-report.md"
            write_report(findings, output)
            text = output.read_text(encoding="utf-8")

        self.assertIn("# C1 科目一题库过时风险审计", text)
        self.assertIn("q1", text)
        self.assertIn("公安部令第163号", text)


if __name__ == "__main__":
    unittest.main()
