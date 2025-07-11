from github import Github
from datetime import datetime, timezone, timedelta
import os

# 認証とリポジトリ取得
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["REPO"])
JST = timezone(timedelta(hours=9))
today_str = datetime.now(JST).strftime("%Y-%m-%d")

# 自分にメンション
USERNAME = os.environ.get("USER_TO_MENTION", "")

# 今日の日付を含む復習Issueを探す
issues = repo.get_issues(state='open', labels=['復習'])
target = None

for issue in issues:
    if f"{today_str}" in issue.title and "復習リスト" in issue.title:
        target = issue
        break

if not target:
    print("🎉 今日の復習対象はありません")
    exit(0)

# チェックリストだけを抜き出す
lines = target.body.splitlines()
checklist_lines = [line for line in lines if line.strip().startswith("- [")]

if not checklist_lines:
    print("✅ チェックリストが空のためスキップ")
    exit(0)

# 本文を組み立てる（本文にはメンション書かない）
body = "\n".join([
    "おはようございます！今日の復習タスクはこちらです：",
    "",
    *checklist_lines,
    "",
    "がんばっていきましょう！💪"
])

# 「今日やるIssue」を作成
title = f"☀️ 今日やる復習リスト - {today_str}"
new_issue = repo.create_issue(title=title, body=body, labels=["今日"])

# メンション通知コメントを追加
if USERNAME:
    new_issue.create_comment(f"{USERNAME} さん、今日の復習タスクが生成されました！📣")
