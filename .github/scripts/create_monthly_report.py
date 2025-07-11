from github import Github
from datetime import datetime, timedelta, timezone
import os
import re
import matplotlib.pyplot as plt

# タイムゾーンと日付の準備
JST = timezone(timedelta(hours=9))
now = datetime.now(JST)
start_of_month = now.replace(day=1)
start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

# GitHub準備
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["REPO"]
g = Github(token)
repo = g.get_repo(repo_name)

# 集計用変数
new_issues = 0
closed_issues = 0
total_reviews = 0

for issue in repo.get_issues(state='all', since=start_of_month):
    if issue.created_at >= start_of_month and issue.created_at < start_of_next_month:
        if "復習" in [label.name for label in issue.labels]:
            new_issues += 1

    if issue.closed_at and start_of_month <= issue.closed_at < start_of_next_month:
        closed_issues += 1

    # 本文に復習回数がある場合、そこから加算
    if issue.body:
        match = re.search(r"<!--\s*復習回数:\s*(\d+)\s*-->", issue.body)
        if match:
            total_reviews += int(match.group(1))

# グラフ作成
labels = ["新規学習", "完了", "復習回数"]
values = [new_issues, closed_issues, total_reviews]
colors = ["#4CAF50", "#2196F3", "#FF9800"]

plt.figure(figsize=(6, 4))
plt.bar(labels, values, color=colors)
plt.title(f"{now.strftime('%Y年%m月')} 学習サマリー")
plt.ylabel("件数")
plt.tight_layout()
graph_path = "/tmp/monthly_summary.png"
plt.savefig(graph_path)

# 画像をアップロードするダミーIssueを作成（非公開）
upload_issue = repo.create_issue(
    title="(temp) graph image upload",
    body="this issue is used to store an image temporarily.",
)
with open(graph_path, "rb") as f:
    comment = upload_issue.create_comment("![summary](https://via.placeholder.com/1)")
    comment.upload_image(f, "monthly_summary.png")

# アップロードした画像URLを取得
uploaded_url = comment.body.split("](")[1].rstrip(")")

# temp issue削除
upload_issue.edit(state="closed")

# 本文生成
report_title = f"📊 {now.strftime('%Y年%m月')}の学習まとめ"
report_body = f"""
# 🎓 {now.strftime('%Y年%m月')}の学習記録まとめ

- 新規学習Issue数: **{new_issues}件**
- 完了したIssue数: **{closed_issues}件**
- 総復習回数: **{total_reviews}回**

![summary-graph]({uploaded_url})

💡 今月もよく頑張りました！来月も継続していきましょう💪
"""

# 最終レポートIssue作成
repo.create_issue(title=report_title, body=report_body, labels=["月次レポート"])
