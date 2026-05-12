import tempfile
import unittest
from pathlib import Path

from scripts.import_questions import (
    normalize_question,
    normalize_questions,
    write_outputs,
)


class ImportQuestionsTest(unittest.TestCase):
    def test_normalizes_true_false_question(self):
        raw = {
            "id": "tf-1",
            "subject": 1,
            "chapterId": 1,
            "question": "机动车应当礼让行人。",
            "answer": "A",
            "answerSkill": "安全文明驾驶。",
            "itemsDescArray": ["正确", "错误"],
        }

        normalized = normalize_question(raw, source_retrieved_at="2026-05-12")

        self.assertEqual(normalized["question_type"], "true_false")
        self.assertEqual(normalized["answer_text"], "正确")
        self.assertEqual(normalized["source"], "DrivingTestSubjectOne")
        self.assertEqual(normalized["stale_risk"], "low")

    def test_preserves_image_url_for_image_questions(self):
        raw = {
            "id": "img-1",
            "subject": 1,
            "chapterId": 1,
            "question": "如图所示，这种标志表示什么？",
            "answer": "A",
            "answerSkill": "看图识别。",
            "itemsDescArray": ["正确", "错误"],
            "url": "https://example.com/sign.jpg",
        }

        normalized = normalize_question(raw, source_retrieved_at="2026-05-12")

        self.assertEqual(normalized["image_url"], "https://example.com/sign.jpg")

    def test_does_not_mark_12_points_as_stale_2_points(self):
        raw = {
            "id": "points-1",
            "subject": 1,
            "chapterId": 1,
            "question": "该违法行为一次记12分。",
            "answer": "A",
            "answerSkill": "现行记分档位。",
            "itemsDescArray": ["正确", "错误"],
        }

        normalized = normalize_question(raw, source_retrieved_at="2026-05-12")

        self.assertEqual(normalized["stale_risk"], "low")

    def test_normalizes_single_choice_question(self):
        raw = {
            "id": "sc-1",
            "subject": "1",
            "chapterId": "1",
            "question": "违反道路交通安全法属于什么行为？",
            "answer": "B",
            "answerSkill": "违反道路交通安全法就是违法行为。",
            "itemsDescArray": ["违章行为", "违法行为", "过失行为", "违规行为"],
        }

        normalized = normalize_question(raw, source_retrieved_at="2026-05-12")

        self.assertEqual(normalized["question_type"], "single_choice")
        self.assertEqual(normalized["answer_text"], "违法行为")
        self.assertIn("chapter:1", normalized["tags"])

    def test_rejects_multi_answer_records(self):
        raw = {
            "id": "bad-1",
            "subject": 1,
            "chapterId": 1,
            "question": "多选题不应进入 C1 科目一模型。",
            "answer": "AB",
            "answerSkill": "",
            "itemsDescArray": ["A", "B", "C", "D"],
        }

        with self.assertRaises(ValueError):
            normalize_question(raw, source_retrieved_at="2026-05-12")

    def test_filters_subject_one_and_writes_metadata(self):
        rows = [
            {
                "id": "one",
                "subject": 1,
                "chapterId": 1,
                "question": "题目1",
                "answer": "A",
                "itemsDescArray": ["正确", "错误"],
            },
            {
                "id": "four",
                "subject": 4,
                "chapterId": 1,
                "question": "题目4",
                "answer": "A",
                "itemsDescArray": ["正确", "错误"],
            },
        ]

        normalized, invalid, metadata = normalize_questions(
            rows, source_retrieved_at="2026-05-12"
        )

        self.assertEqual(len(normalized), 1)
        self.assertEqual(invalid, [])
        self.assertEqual(metadata["processed_subject1_count"], 1)
        self.assertEqual(metadata["raw_count"], 2)

        with tempfile.TemporaryDirectory() as tmpdir:
            write_outputs(normalized, invalid, metadata, Path(tmpdir))
            self.assertTrue((Path(tmpdir) / "questions.json").exists())
            self.assertTrue((Path(tmpdir) / "questions.csv").exists())
            self.assertTrue((Path(tmpdir) / "metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
