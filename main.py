import argparse
from pathlib import Path

from mofeapi.client import Client

from upload import upload_sample_explanations, upload_testcases
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
            upload_testcases(client, problem_config, Path("testcases.zip"))
            # テストケースをアップロードしたら zip ファイルを削除する
            Path("testcases.zip").unlink()

        # いずれかのアップロードが行われた場合、テストケースの説明をアップロードする
        if args.upload_statement or args.upload_testcases:
            upload_sample_explanations(client, problem_id, path / "tests")
