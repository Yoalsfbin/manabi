from github import Github
from datetime import datetime, timedelta, timezone
import os
import re

# タイムゾーンと日付
JST = timezone(timedelta(hours=9))
now = datetime.now(JST)
start_of_month = now.replace(day=1)
start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

# GitHub認証
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["REPO"]
repo = Github(token).get_repo(repo_name)

# 集計変数
new_issues = 0
closed_issues = 0
total_reviews = 0

for issue in repo.get_issues(state='all', since=start_of_month):
    if issue.created_at and start_of_month <= issue.created_at < start_of_next_month:
        if "復習" in [label.name for label in issue.labels]:
            new_issues += 1

    if issue.closed_at and start_of_month <= issue.closed_at < start_of_next_month:
        closed_issues += 1

    if issue.body:
        match = re.search(r"<!--\s*復習回数:\s*(\d+)\s*-->", issue.body)
        if match:
            total_reviews += int(match.group(1))

# レポートIssue本文
title = f"📊 {now.strftime('%Y年%m月')}の学習まとめ"
body = f"""
# 🎓 {now.strftime('%Y年%m月')}の学習記録まとめ

- 新規学習Issue数: **{new_issues}件**
- 完了したIssue数: **{closed_issues}件**
- 総復習回数: **{total_reviews}回**

💡 今月もよく頑張りました！来月も継続していきましょう💪
"""

repo.create_issue(title=title, body=body, labels=["月次レポート"])
