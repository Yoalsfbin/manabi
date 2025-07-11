from github import Github
from datetime import datetime, timezone, timedelta
import os

g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ["REPO"])
USERNAME = os.environ.get("GITHUB_USER_TO_MENTION", "")
JST = timezone(timedelta(hours=9))

today_str = datetime.now(JST).strftime("%Y-%m-%d")

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

# 本文からチェックリスト部分を抽出
lines = target.body.splitlines()
checklist_lines = [line for line in lines if line.strip().startswith("- [")]

if not checklist_lines:
    print("✅ チェックリストが空のためスキップ")
    exit(0)

# 今日やるIssueを作成
title = f"☀️ 今日やる復習リスト - {today_str}"
body = "\n".join([
    f"{USERNAME}",
    "",
    "おはようございます！今日の復習タスクはこちらです：",
    "",
    *checklist_lines,
    "",
    "がんばっていきましょう！💪"
])

repo.create_issue(title=title, body=body, labels=["今日"])
