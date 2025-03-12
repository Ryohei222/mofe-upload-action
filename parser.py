import re
import tomllib

from mofeapi.enums import AggregateType, Difficulty
from mofeapi.models.testcase import TestcaseSetBase

from exceptions import (
    ConstraintsNotFoundError,
    InputFormatNotFoundError,
    OutputFormatNotFoundError,
    StatementNotFoundError,
    TitleNotFoundError,
)
from models import ProblemConfig, Statement


def find_first_match(content: str, pattern: re.Pattern) -> str:
    matches = pattern.search(content)
    if not matches:
        raise AttributeError("Pattern did not match any content.")
    return matches.group(1).strip()


def parse_statement_md(md_content: str) -> Statement:
    name_pattern = re.compile(r"# (.+)\n")
    statement_pattern = re.compile(r"## 問題文\n(.+?)## 制約", re.DOTALL)
    constraints_pattern_with_partial_scores = re.compile(r"## 制約\n(.+?)### 部分点", re.DOTALL)
    constraints_pattern = re.compile(r"## 制約\n(.+?)## 入力", re.DOTALL)
    partial_scores_pattern = re.compile(r"### 部分点\n(.+?)## 入力", re.DOTALL)
    input_format_pattern = re.compile(r"## 入力\n(.+?)## 出力", re.DOTALL)
    output_format_pattern_with_sample = re.compile(r"## 出力\n(.+?)### 入力例", re.DOTALL)
    output_format_pattern = re.compile(r"## 出力\n(.+?)$", re.DOTALL)

    try:
        name = find_first_match(md_content, name_pattern)
    except AttributeError:
        raise TitleNotFoundError()

    try:
        statement = find_first_match(md_content, statement_pattern)
    except AttributeError:
        raise StatementNotFoundError()

    try:
        # 部分点が存在する場合 ## 制約 の後に ### 部分点 が来る
        # 部分点が存在しない場合 ## 制約 の後に ## 入力 が来る
        if constraints_pattern_with_partial_scores.search(md_content):
            constraints = find_first_match(md_content, constraints_pattern_with_partial_scores)
        else:
            constraints = find_first_match(md_content, constraints_pattern)
    except AttributeError:
        raise ConstraintsNotFoundError()

    partial_scores = None
    if partial_scores_pattern.search(md_content):
        partial_scores = find_first_match(md_content, partial_scores_pattern)

    try:
        input_format = find_first_match(md_content, input_format_pattern)
    except AttributeError:
        raise InputFormatNotFoundError()

    try:
        if output_format_pattern_with_sample.search(md_content):
            output_format = find_first_match(md_content, output_format_pattern_with_sample)
        else:
            output_format = find_first_match(md_content, output_format_pattern)
    except AttributeError:
        raise OutputFormatNotFoundError()

    return Statement(
        name=name,
        statement=statement,
        constraints=constraints,
        input_format=input_format,
        output_format=output_format,
        partial_scores=partial_scores,
    )


def parse_problem_toml(problem_toml_content: str) -> ProblemConfig:
    data = tomllib.loads(problem_toml_content)
    if "id" not in data:
        raise ValueError(
            'コンテスト内の ID が設定されていません。problem.toml に id = "コンテスト内の ID" という行を追加してください。'
        )
    if "mofe" not in data:
        raise ValueError(
            "MOFE 用の設定が見つかりません。problem.toml に [mofe] というセクションがあるか確認してください。"
        )
    if "testcase_sets" not in data["mofe"]:
        raise ValueError(
            "テストケースセットの設定が見つかりません。problem.toml に [mofe.testcase_sets] というセクションがあるか確認してください。"
        )

    testcase_sets_with_regex = []
    for testcase_set_name, testcase_set in data["mofe"]["testcase_sets"].items():
        testcase_set = testcase_set[0]
        testcase_sets_with_regex.append(
            (
                testcase_set["regex"],
                TestcaseSetBase(
                    aggregate_type=AggregateType.ALL,
                    name=testcase_set_name,
                    points=testcase_set["points"],
                ),
            )
        )

    return ProblemConfig(
        position_in_contest=data["id"],
        problem_id=data["mofe"]["problem_id"],
        difficulty=Difficulty(data["mofe"]["difficulty"]),
        execution_time_limit=data["mofe"]["execution_time_limit"],
        submission_limit_1=data["mofe"]["submission_limit_1"],
        submission_limit_2=data["mofe"]["submission_limit_2"],
        testcase_sets_with_regex=testcase_sets_with_regex,
    )
