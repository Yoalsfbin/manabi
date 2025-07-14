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

# ================================
# 🟡 執筆中の open issue を取得
# ================================
editing_issues = [
    issue for issue in repo.get_issues(state="open", labels=["執筆中"])
    if not issue.pull_request
]

editing_section = ""
if editing_issues:
    editing_section_lines = [
        "⚠️ **現在、以下の Issue は「執筆中」です**",
        "",
    ]
    for issue in editing_issues:
        editing_section_lines.append(
            f"- [#{issue.number} {issue.title}](https://github.com/{repo.full_name}/issues/{issue.number})"
        )
    editing_section = "\n".join(editing_section_lines) + "\n\n"

# ================================
# 📚 今日の復習リストを取得
# ================================
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

# ================================
# ☀️ 本文を組み立てて Issue 作成
# ================================
body_lines = [
    "おはようございます！今日の復習タスクはこちらです：",
    "",
]

if editing_section:
    body_lines.append(editing_section)

body_lines += checklist_lines
body_lines.append("")
body_lines.append("がんばっていきましょう！💪")

body = "\n".join(body_lines)

# 「今日やるIssue」を作成
title = f"☀️ 今日やる復習リスト - {today_str}"
new_issue = repo.create_issue(title=title, body=body, labels=["今日"])

# メンション通知コメント（状況に応じて分岐）
if USERNAME:
    if editing_issues:
        new_issue.create_comment(
            f"{USERNAME} さん、今日の復習リストが生成されました！📚\n"
            f"現在進行中のIssueもあります。無理せずコツコツいきましょう ✏️💪"
        )
    else:
        new_issue.create_comment(
            f"{USERNAME} さん、今日の復習タスクが生成されました！📣\n"
            f"今日は集中して取り組めそうです！がんばっていきましょう 💪"
        )
