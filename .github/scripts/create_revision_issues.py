from github import Github
from datetime import datetime, timedelta, timezone
import os
import re

REPO_NAME = os.environ["REPO"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
repo = Github(GITHUB_TOKEN).get_repo(REPO_NAME)

JST = timezone(timedelta(hours=9))
now = datetime.utcnow().replace(tzinfo=timezone.utc)
today_str = now.astimezone(JST).strftime("%Y-%m-%d")

# 復習のスケジュール（作成から○日後）
review_days = [0, 3, 7, 14, 30, 60, 90]

# 復習対象を日数ごとに収集
for day in review_days:
    target = []

    for issue in repo.get_issues(state="open"):
        if issue.pull_request is not None:
            continue  # PRは除外
        if "復習" not in [label.name for label in issue.labels]:
            continue  # 復習ラベルなしは対象外

        created_at = issue.created_at.replace(tzinfo=timezone.utc)
        days_ago = (now.date() - created_at.date()).days

        if days_ago == day:
            target.append(issue)

    if not target:
        continue

    # Issue本文を生成
    body_lines = [
        f"このIssueは作成から **{day}日後** の復習対象です。",
        f"",
        f"📅 今日の日付: {today_str}",
        "",
        "### 対象Issue一覧:",
    ]

    for issue in target:
        # 復習回数の記録を確認
        body = issue.body or ""
        match = re.search(r"<!--\s*復習回数:\s*(\d+)\s*-->", body)
        count = int(match.group(1)) + 1 if match else 1

        # 元Issueを更新して復習回数を記録
        new_body = re.sub(
            r"<!--\s*復習回数:\s*\d+\s*-->",
            f"<!-- 復習回数: {count} -->",
            body
        ) if match else body + f"\n\n<!-- 復習回数: {count} -->"

        issue.edit(body=new_body)

        # チェックリストとして追加
        body_lines.append(f"- [ ] [#{issue.number} {issue.title}](https://github.com/{REPO_NAME}/issues/{issue.number}) （{count}回目の復習）")

    # 新しい復習Issueを作成
    title = f"📚 復習リスト（{day}日目） - {today_str}"
    body = "\n".join(body_lines)
    repo.create_issue(title=title, body=body, labels=["復習"])
