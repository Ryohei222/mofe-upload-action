import re
from pathlib import Path

from mofeapi.client import Client

from models import ProblemConfig


def upload_testcases(client: Client, problem_config: ProblemConfig, testcases_zip_path: Path) -> None:
    problem_id = problem_config.problem_id
    # すでに存在するテストケースをすべて削除する
    old_testcase_sets, old_testcases = client.get_testcases(problem_id)
    client.delete_multiple_testcases(problem_id, [testcase.id for testcase in old_testcases])

    # テストケースセットを削除する
    for testcase_set in old_testcase_sets:
        if testcase_set.name == "sample" or testcase_set.name == "all":
            continue
        client.delete_testcase_set(problem_id, testcase_set.id)

    # テストケースをアップロードする
    with open("testcases.zip", "rb") as f:
        client.upload_testcases(problem_id, f.read())

    # アップロードしたテストケースを取得する
    new_testcase_sets, new_testcases = client.get_testcases(problem_id)

    # 各テストケースセットについて、
    # 1. そのセットがすでに MOFE 上に存在するか判定する
    #     a. 存在する場合はそのセットの ID を取得し、points と aggregate_type を更新する
    #     b. 存在しない場合はそのセットを作成する
    # 2. 正規表現にマッチするテストケースを取得し、テストケースセットに追加する

    for regex_pattern, testcase_set_base in problem_config.testcase_sets_with_regex:
        for existing_testcase_set_base in new_testcase_sets:
            if existing_testcase_set_base.name == testcase_set_base.name:
                testcase_set_id = existing_testcase_set_base.id
                client.update_testcase_set(problem_id, testcase_set_id, testcase_set_base)
                break
        else:
            client.create_testcase_set(problem_id, testcase_set_base)

        testcase_ids = []
        for testcase in new_testcases:
            if re.match(re.compile(regex_pattern), testcase.name):
                testcase_ids.append(testcase.id)
        client.add_to_testcase_set_multiple(problem_id, testcase_set_id, testcase_ids)


def upload_sample_explanations(client: Client, problem_id: int, samples_path: Path) -> None:
    _, testcases = client.get_testcases(problem_id)
    # sample_path 直下に存在する .md ファイルを列挙する
    for explanation_path in samples_path.glob("*.md"):
        md = open(explanation_path, "r").read()
        testcase_name = explanation_path.stem
        # 拡張子を除いたファイル名と一致するテストケースを探索する
        testcase_ids = [testcase.id for testcase in testcases if testcase.name == testcase_name]
        if len(testcase_ids) == 0:
            continue
        testcase_id = testcase_ids[0]
        testcase = client.get_testcase(problem_id, testcase_id)
        testcase.explanation = md
        client.update_testcase(problem_id, testcase_id, testcase)
