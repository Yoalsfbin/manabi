from github import Github
from datetime import datetime, timedelta, timezone
import os
import re

# タイムゾーン設定（JST）
JST = timezone(timedelta(hours=9))
now = datetime.now(JST)

# 前月の期間を取得
start_of_this_month = now.replace(day=1)
start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
end_of_last_month = start_of_this_month

# GitHub 認証
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["REPO"]
repo = Github(token).get_repo(repo_name)

# レポートタイトル
report_month_str = start_of_last_month.strftime('%Y年%m月')
title = f"📊 {report_month_str}の学習まとめ"

# 既存Issueに同名タイトルがあるか確認
existing_issues = repo.get_issues(state='all', since=start_of_last_month)
for issue in existing_issues:
    if issue.title == title:
        print("✅ 既に今月のレポートが作成されています。スキップします。")
        exit(0)

# 集計用変数
new_issues = 0
closed_issues = 0
total_reviews = 0

# 前月分のデータを集計
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

# Issue作成
repo.create_issue(title=title, body=body, labels=["月次レポート"])
print("✅ レポートIssueを作成しました。")
