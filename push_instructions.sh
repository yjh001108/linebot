# push_instructions.sh - 在本機上推送專案到 GitHub 的範例指令
# 1) 建立本地 repo 並初始提交
git init
git add .
git commit -m "Initial commit - LINE bookkeeping template"

# 2) 在 GitHub 建立一個空的 repository，例如 "linebookkeeping-template"
#    然後將 remote 新增到本地
# 如果使用 HTTPS:
# git remote add origin https://github.com/USERNAME/REPO.git
# 如果使用 SSH:
# git remote add origin git@github.com:USERNAME/REPO.git

# 3) 推送到 GitHub
git branch -M main
git push -u origin main

# 如果你想使用 GitHub CLI (gh)
# gh repo create USERNAME/REPO --public --source=. --remote=origin --push
