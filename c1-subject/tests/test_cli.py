import tempfile
import unittest
from pathlib import Path

from cli.study import filter_questions, record_wrong_answer, search_questions


QUESTIONS = [
    {"id": "1", "question": "扣分题", "options": ["A", "B"], "answer": "A", "answer_text": "A", "answer_skill": "记分", "tags": ["扣分"], "topic": "points"},
    {"id": "2", "question": "交通标志", "options": ["A", "B"], "answer": "B", "answer_text": "B", "answer_skill": "标志", "tags": ["标志"], "topic": "signs"},
]


class StudyCliTest(unittest.TestCase):
    def test_searches_question_text_tags_and_explanation(self):
        self.assertEqual([q["id"] for q in search_questions(QUESTIONS, "扣分")], ["1"])
        self.assertEqual([q["id"] for q in search_questions(QUESTIONS, "标志")], ["2"])

    def test_filters_by_tag_or_topic(self):
        self.assertEqual([q["id"] for q in filter_questions(QUESTIONS, tag="扣分")], ["1"])
        self.assertEqual([q["id"] for q in filter_questions(QUESTIONS, topic="signs")], ["2"])

    def test_records_wrong_answer_once(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            review_path = Path(tmpdir) / "review.json"
            record_wrong_answer(review_path, QUESTIONS[0], "B")
            record_wrong_answer(review_path, QUESTIONS[0], "B")
            text = review_path.read_text(encoding="utf-8")
            self.assertEqual(text.count('"id": "1"'), 1)


if __name__ == "__main__":
    unittest.main()
