#!/bin/bash
# 宅趣网站自动部署脚本
# 用法：./deploy.sh "更新说明"

MESSAGE=${1:-"自动更新网站"}

echo "🚀 开始部署宅趣网站..."

# 检查 Git 是否配置
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装，请先安装 Git"
    exit 1
fi

# 进入网站目录
cd /home/admin/.openclaw/workspace/zhaiqu-website

# 初始化 Git（如果是第一次）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
    git add .
    git commit -m "初始提交：宅趣网站"
    echo "✅ Git 仓库已初始化"
    echo ""
    echo "📋 下一步："
    echo "1. 在 GitHub 创建新仓库：https://github.com/new"
    echo "2. 仓库名：zhaiqu-website"
    echo "3. 然后运行："
    echo "   git remote add origin https://github.com/你的用户名/zhaiqu-website.git"
    echo "   git push -u origin main"
    exit 0
fi

# 提交并推送
echo "📝 提交更改..."
git add .
git commit -m "$MESSAGE"

echo "🚀 推送到 GitHub..."
git push

echo ""
echo "✅ 部署完成！"
echo "网站将在几分钟后自动更新"
echo "访问：https://你的用户名.github.io/zhaiqu-website"
