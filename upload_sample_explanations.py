from pathlib import Path

from mofeapi.client import Client


def upload_sample_explanations(client: Client, problem_id: int, samples_path: Path):
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
