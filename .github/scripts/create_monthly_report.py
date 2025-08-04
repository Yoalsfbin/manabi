from github import Github
from datetime import datetime, timedelta, timezone
import os
import re

# JSTタイムゾーン
JST = timezone(timedelta(hours=9))
now = datetime.now(JST)

# 先月の開始と終了
start_of_this_month = now.replace(day=1)
start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
end_of_last_month = start_of_this_month

# GitHub認証
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["REPO"]
repo = Github(token).get_repo(repo_name)

# レポートタイトル（日付は先月）
report_month_str = start_of_last_month.strftime('%Y年%m月')
title = f"📊 {report_month_str}の学習まとめ"

# 重複チェック
existing_issues = repo.get_issues(state='all', since=start_of_last_month)
for issue in existing_issues:
    if issue.title == title:
        print(f"⚠️ 既に {title} は作成済み。スキップします。")
        exit(0)

# 集計
new_issues = 0
closed_issues = 0
total_reviews = 0

for issue in repo.get_issues(state='all', since=start_of_last_month):
    if issue.created_at and start_of_last_month <= issue.created_at < end_of_last_month:
        if "復習" in [label.name for label in issue.labels]:
            new_issues += 1

    if issue.closed_at and start_of_last_month <= issue.closed_at < end_of_last_month:
        closed_issues += 1

    if issue.body:
        match = re.search(r"<!--\s*復習回数:\s*(\d+)\s*-->", issue.body)
        if match:
            total_reviews += int(match.group(1))

# レポート本文
body = f"""
# 🎓 {report_month_str}の学習記録まとめ

- 新規学習Issue数: **{new_issues}件**
- 完了したIssue数: **{closed_issues}件**
- 総復習回数: **{total_reviews}回**

💡 よく頑張りました！次の月も継続していきましょう💪
"""

# レポート作成
repo.create_issue(title=title, body=body, labels=["月次レポート"])
print(f"✅ {title} を作成しました。")
