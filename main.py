import argparse
from logging import Formatter, StreamHandler, getLogger
from pathlib import Path
from sys import stdout

from mofeapi.client import Client

from upload import upload_sample_explanations, upload_testcases
from util import build_problem_params, compress_testcases, load_problem_toml, load_statement, log_problem_diff

logger = getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("mofe_username", type=str, help="MOFEのユーザー名")
    parser.add_argument("mofe_password", type=str, help="MOFEのパスワード")
    parser.add_argument("--upload-testcases", type=str, help="テストケースをアップロードするかどうか", default="true")
    parser.add_argument("--upload-statement", type=str, help="問題文をアップロードするかどうか", default="true")
    parser.add_argument(
        "--force-upload-statement", type=str, help="問題文を強制的にアップロードするかどうか", default="false"
    )
    parser.add_argument("--use-debug-logging", type=str, help="デバッグログを出力するかどうか", default="false")

    args = parser.parse_args()

    flag_upload_testcases = args.upload_testcases.lower() == "true"
    flag_upload_statement = args.upload_statement.lower() == "true"
    flag_force_upload_statement = args.force_upload_statement.lower() == "true"
    flag_use_debug_logging = args.use_debug_logging.lower() == "true"

    if flag_use_debug_logging:

        formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = StreamHandler(stream=stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel("DEBUG")

    logger.debug("upload-testcases: %s", flag_upload_testcases)
    logger.debug("upload-statement: %s", flag_upload_statement)
    logger.debug("force-upload-statement: %s", flag_force_upload_statement)
    logger.debug("use-debug-logging: %s", flag_use_debug_logging)

    client = Client()
    client.login(args.mofe_username, args.mofe_password)

    for path in Path(".").glob("*"):
        # problem.toml が配置されているディレクトリのみを対象とする
        if not path.is_dir() or not (path / "problem.toml").exists():
            continue

        logger.info('Processing "%s"', path)

        # problem.toml を読み込む
        problem_config = load_problem_toml(path / "problem.toml")
        problem_id = problem_config.problem_id
        position_in_contest = problem_config.position_in_contest

        # 問題文をアップロードする場合
        if flag_upload_statement:
            statement = load_statement(path / "ss-out" / f"{position_in_contest}.md")
            problem_params = build_problem_params(statement, problem_config)

            # MOFE 上に存在する問題名と markdown の問題名が一致するかチェックする
            problem_on_mofe = client.get_problem(problem_id)
            if not flag_force_upload_statement:
                if problem_on_mofe.name != problem_params.name:
                    raise ValueError("MOFE 上の問題名と問題文の問題名が一致しません")

            client.update_problem(problem_id, problem_params)
            updated_problem = client.get_problem(problem_id)
            log_problem_diff(problem_on_mofe, updated_problem)

        # テストケースをアップロードする場合
        if flag_upload_testcases:
            # テストケースを zip に圧縮する
            compress_testcases(path)
            upload_testcases(client, problem_config, Path("testcases.zip"))
            # テストケースをアップロードしたら zip ファイルを削除する
            Path("testcases.zip").unlink()

        # いずれかのアップロードが行われた場合、テストケースの説明をアップロードする
        if flag_upload_statement or flag_upload_testcases:
            upload_sample_explanations(client, problem_id, path / "tests")
