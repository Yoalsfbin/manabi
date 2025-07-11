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
        match =
