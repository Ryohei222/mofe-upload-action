from dataclasses import dataclass
from typing import List, Optional

from mofeapi.enums import Difficulty
from mofeapi.models.testcase import TestcaseSetBase


@dataclass
class Statement:
    name: str
    statement: str
    constraints: str
    input_format: str
    output_format: str
    partial_scores: Optional[str]


@dataclass
class TestcaseSetWithRegex:
    regex: str
    testcase_set: TestcaseSetBase


@dataclass
class ProblemConfig:
    problem_id: int
    difficulty: Difficulty
    execution_time_limit: int
    submission_limit_1: int
    submission_limit_2: int
    position_in_contest: str
    testcase_sets: List[TestcaseSetWithRegex]
