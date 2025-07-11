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
repo = Git
