import os
import shutil
from logging import getLogger
from parser import ProblemConfig, Statement, parse_problem_toml, parse_statement_md
from pathlib import Path

from mofeapi.models.problem import ProblemDetail, ProblemParams

logger = getLogger(__name__)


def compress_testcases(problem_path: Path) -> None:
    testcase_path = problem_path / "testcase"

    os.mkdir(testcase_path)
    os.mkdir(testcase_path / "input")
    os.mkdir(testcase_path / "output")

    testcase_count = 0

    for path in (problem_path / "rime-out/tests").glob("*.in"):
        casename = path.name[:-3]
        shutil.copy(path, testcase_path / "input" / (casename + ".txt"))
        shutil.copy(str(path)[:-3] + ".diff", testcase_path / "output" / (casename + ".txt"))
        testcase_count += 1

    shutil.make_archive("testcases", format="zip", root_dir=testcase_path)
    shutil.rmtree(str(testcase_path))


def build_problem_params(statement: Statement, problem_config: ProblemConfig) -> ProblemParams:
    return ProblemParams(
        name=statement.name,
        statement=statement.statement,
        constraints=statement.constraints,
        input_format=statement.input_format,
        output_format=statement.output_format,
        partial_scores=statement.partial_scores,
        difficulty=problem_config.difficulty,
        execution_time_limit=problem_config.execution_time_limit,
        submission_limit_1=problem_config.submission_limit_1,
        submission_limit_2=problem_config.submission_limit_2,
    )


def load_problem_toml(problem_toml_path: Path) -> ProblemConfig:
    if not problem_toml_path.exists():
        raise FileNotFoundError(f"problem.toml not found in {problem_toml_path}")
    problem_toml = open(problem_toml_path, "r").read()
    return parse_problem_toml(problem_toml)


def load_statement(statement_md_path: Path) -> Statement:
    if not statement_md_path.exists():
        raise FileNotFoundError(f"statement.md not found in {statement_md_path}")
    statement_md = open(statement_md_path, "r").read()
    return parse_statement_md(statement_md)


def log_problem_diff(old_problem: ProblemDetail, new_problem: ProblemDetail) -> None:

    def log_diff(field_name: str, old_value, new_value):
        if old_value != new_value:
            logger.info(f"{field_name} が更新されました")
            logger.info(f"old: {old_value}")
            logger.info(f"new: {new_value}")

    log_diff("問題名", old_problem.name, new_problem.name)
    log_diff("問題文", old_problem.statement, new_problem.statement)
    log_diff("制約", old_problem.constraints, new_problem.constraints)
    log_diff("入力形式", old_problem.input_format, new_problem.input_format)
    log_diff("出力形式", old_problem.output_format, new_problem.output_format)
    log_diff("部分点", old_problem.partial_scores, new_problem.partial_scores)
    log_diff("難易度", old_problem.difficulty, new_problem.difficulty)
    log_diff("実行時間制限", old_problem.execution_time_limit, new_problem.execution_time_limit)
    log_diff("1 つ前からの提出制限", old_problem.submission_limit_1, new_problem.submission_limit_1)
    log_diff("2 つ前からの提出制限", old_problem.submission_limit_2, new_problem.submission_limit_2)
