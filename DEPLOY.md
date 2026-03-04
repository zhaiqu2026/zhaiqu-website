# 🚀 宅趣网站部署指南

## ✅ 已完成
- [x] 网站代码已创建 (`index.html`)
- [x] 品牌名：宅趣
- [x] 域名：zhaiqu.fun

---

## 📋 部署方案（3 选 1）

### 方案 A：Netlify Drop（最简单！5 分钟上线）⭐推荐

1. **访问** https://app.netlify.com/drop

2. **注册/登录** Netlify（可以用 GitHub 账号）

3. **拖拽文件** 
   - 打开文件管理器
   - 找到 `/home/admin/.openclaw/workspace/zhaiqu-website/index.html`
   - 拖到 Netlify Drop 页面

4. **完成！** 网站立刻上线，你会得到一个临时域名

5. **绑定域名**（可选）
   - 在 Netlify 后台点击 "Domain settings"
   - 添加 `zhaiqu.fun`
   - 按提示配置 DNS

---

### 方案 B：Vercel CLI（命令行部署）

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录 Vercel
vercel login

# 3. 进入网站目录
cd /home/admin/.openclaw/workspace/zhaiqu-website

# 4. 部署
vercel --prod

# 5. 绑定域名（在 Vercel 后台操作）
```

---

### 方案 C：GitHub + Vercel（最专业）

1. 创建 GitHub 仓库
2. 上传 `index.html`
3. 在 Vercel 导入 GitHub 项目
4. 自动部署

---

## 🎨 自定义网站内容

编辑 `index.html`，修改以下内容：

- **商品名称**：搜索"商品名称 1"，替换成你的商品
- **商品价格**：搜索"¥99"，替换成实际价格
- **商品描述**：搜索"这里是商品的详细描述"
- **联系方式**：搜索"你的微信号"，替换成你的微信/电话
- **品牌介绍**：搜索"关于宅趣"下面的文字

---

## 📞 需要帮助？

随时联系！
