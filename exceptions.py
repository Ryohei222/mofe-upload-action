class StatementFormatError(Exception):
    """問題文のフォーマットに関する例外"""

    def __init__(self, message):
        message = "問題文のフォーマットが正しくありません。\n\n " + message
        super().__init__(message)


class TitleNotFoundError(StatementFormatError):
    def __init__(self):
        message = "問題名が見つかりません。`# {問題名}` という行があるか確認してください。"
        super().__init__(message)


class StatementNotFoundError(StatementFormatError):
    def __init__(self):
        message = "問題文が見つかりません。`## 問題文` という行があることと、`## 制約` が `## 問題文` の次の見出しであることを確認してください。"
        super().__init__(message)


class ConstraintsNotFoundError(StatementFormatError):
    def __init__(self):
        message = "制約が見つかりません。`## 制約` という行があることと、(`## 入力` | `### 部分点`) が `## 制約` の次の見出しであることを確認してください。"
        super().__init__(message)


class InputFormatNotFoundError(StatementFormatError):
    def __init__(self):
        message = "入力形式の説明が見つかりません。`## 入力` という行があることと、`## 出力` が `## 入力` の次の見出しであることを確認してください。"
        super().__init__(message)


class OutputFormatNotFoundError(StatementFormatError):
    def __init__(self):
        message = "出力形式の説明が見つかりません。`## 出力` という行があるか確認してください。"
        super().__init__(message)
