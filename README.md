# mofe-upload-action

## 概要

GitHub 上の問題文とテストケースを [MOFE](https://mofecoder.com/) 上にアップロードします。

## 要件

GitHub Actions で [statements-manager](https://github.com/tsutaj/statements-manager) と [rime](https://github.com/icpc-jag/rime) を用いた自動テストを行っているものとします。


## 使い方

1. MOFE へのアップロードに用いるアカウントの認証情報を Repository secrets に設定する。
2. MOFE 上に空の問題を作成し、問題 ID を取得する。
3. `problem.toml` に次の項目を追記する。
    - MOFE の問題の設定
        - 問題 ID
        - 難易度
        - 実行時間制限
        - 提出頻度の制限
    - テストケースセットの情報
        - テストケースセットの名前
        - 配点
        - 該当するテストケースの名前にマッチする正規表現
        - 集約タイプ
4. 自動テストを行っている GitHub Actions の job の step に `mofe-upload-action` を追加する

- [`problem.toml` の設定例](https://github.com/Ryohei222/mofe-upload-action-test/blob/main/a-plus-b/problem.toml)
- [job の設定例](https://github.com/Ryohei222/mofe-upload-action-test/blob/main/.github/workflows/test.yml)
