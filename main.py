import argparse
import re
from pathlib import Path

from mofeapi.client import Client

from upload_sample_explanations import upload_sample_explanations
from util import build_problem_params, compress_testcases, load_problem_toml, load_statement

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("mofe_username", type=str, help="MOFEのユーザー名")
    parser.add_argument("mofe_password", type=str, help="MOFEのパスワード")
    parser.add_argument("--upload-testcases", type=bool, help="テストケースをアップロードするかどうか", default=True)
    parser.add_argument("--upload-statement", type=bool, help="問題文をアップロードするかどうか", default=True)
    parser.add_argument(
        "--force-upload-statement", type=bool, help="問題文を強制的にアップロードするかどうか", default=False
    )

    args = parser.parse_args()

    client = Client()
    client.login(args.mofe_username, args.mofe_password)

    for path in Path(".").glob("*"):
        # problem.toml が配置されているディレクトリのみを対象とする
        if not path.is_dir() or not (path / "problem.toml").exists():
            continue

        # problem.toml を読み込む
        problem_config = load_problem_toml(path / "problem.toml")
        problem_id = problem_config.problem_id
        position_in_contest = problem_config.position_in_contest

        # 問題文をアップロードする場合
        if args.upload_statement:
            # 問題文を読み込む
            statement = load_statement(path / "ss-out" / f"{position_in_contest}.md")
            problem_params = build_problem_params(statement, problem_config)

            # MOFE 上に存在する問題名と markdown の問題名が一致するかチェックする
            if not args.force_upload_statement:
                problem_on_mofe = client.get_problem(problem_id)
                if problem_on_mofe.name != problem_params.name:
                    raise ValueError("MOFE 上の問題名と問題文の問題名が一致しません")

            client.update_problem(problem_id, problem_params)

        # テストケースをアップロードする場合
        if args.upload_testcases:

            # テストケースを zip に圧縮する
            compress_testcases(path)

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

        # 問題文をアップロードした場合、テストケースの説明をアップロードする
        if args.upload_statement:
            upload_sample_explanations(client, problem_id, path / "tests")
