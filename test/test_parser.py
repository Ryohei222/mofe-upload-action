import logging
from parser import parse_problem_toml
from sys import stdout
from unittest import TestCase

from mofeapi.enums import AggregateType, Difficulty


class TestParseProblemToml(TestCase):
    def setUp(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.StreamHandler(stdout)
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
        logging.root.setLevel("DEBUG")
        return super().setUp()

    def test_parse_problem_toml_valid(self):
        problem_toml_content = """
        id = "A"

        [constraints]
        MIN_N = 1
        MAX_N = 100000

        [mofe]
        problem_id = 9999
        difficulty = "Benihuki"
        execution_time_limit = 2000
        submission_limit_1 = 5
        submission_limit_2 = 60

        [[mofe.testcase_sets]]
        name = "sample"
        regex = "00_sample_\\\\d+"
        points = 0
        aggregate_type = "all"

        [[mofe.testcase_sets]]
        name = "all"
        regex = "."
        points = 100
        aggregate_type = "all"
        """
        config = parse_problem_toml(problem_toml_content)
        self.assertEqual(config.position_in_contest, "A")
        self.assertEqual(config.problem_id, 9999)
        self.assertEqual(config.difficulty, Difficulty.BENIHUKI)
        self.assertEqual(config.execution_time_limit, 2000)
        self.assertEqual(config.submission_limit_1, 5)
        self.assertEqual(config.submission_limit_2, 60)
        self.assertEqual(len(config.testcase_sets), 2)
        self.assertEqual(config.testcase_sets[0].regex, "00_sample_\\d+")
        self.assertEqual(config.testcase_sets[0].testcase_set.name, "sample")
        self.assertEqual(config.testcase_sets[0].testcase_set.points, 0)
        self.assertEqual(config.testcase_sets[0].testcase_set.aggregate_type, AggregateType.ALL)
        self.assertEqual(config.testcase_sets[1].testcase_set.name, "all")
        self.assertEqual(config.testcase_sets[1].regex, ".")
        self.assertEqual(config.testcase_sets[1].testcase_set.points, 100)
        self.assertEqual(config.testcase_sets[1].testcase_set.aggregate_type, AggregateType.ALL)

    def test_parse_problem_toml_missing_id(self):
        problem_toml_content = """
        [mofe]
        problem_id = 9999
        difficulty = "Benihuki"
        execution_time_limit = 2000
        submission_limit_1 = 5
        submission_limit_2 = 60

        [[mofe.testcase_sets]]
        name = "sample"
        regex = "00_sample_\\\\d+"
        points = 0
        aggregate_type = "all"
        """
        with self.assertRaises(ValueError) as context:
            parse_problem_toml(problem_toml_content)
        self.assertIn("コンテスト内の ID が設定されていません", str(context.exception))

    def test_parse_problem_toml_missing_mofe(self):
        problem_toml_content = """
        id = "A"
        """
        with self.assertRaises(ValueError) as context:
            parse_problem_toml(problem_toml_content)
        self.assertIn("MOFE 用の設定が見つかりません", str(context.exception))

    def test_parse_problem_toml_missing_testcase_sets(self):
        problem_toml_content = """
        id = "A"

        [mofe]
        problem_id = 9999
        difficulty = "Benihuki"
        execution_time_limit = 2000
        submission_limit_1 = 5
        submission_limit_2 = 60
        """
        with self.assertRaises(ValueError) as context:
            parse_problem_toml(problem_toml_content)
        self.assertIn("テストケースセットの設定が見つかりません", str(context.exception))
