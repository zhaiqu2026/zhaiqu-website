# 🤖 1688 自动抓取系统

## 文件说明

- `auto-fetch-1688.py` - 主脚本，自动抓取 1688 商品信息
- `products.json` - 抓取的商品数据（运行后生成）
- `cookies.json` - 登录 Cookies（首次登录后保存）

## 使用方法

### 首次运行（需要登录）

```bash
cd /home/admin/.openclaw/workspace/zhaiqu-website
python3 auto-fetch-1688.py
```

**首次运行会提示需要登录**，有两种方式：

#### 方式 1：手动登录后导出 Cookies（推荐）

1. 用浏览器访问 https://detail.1688.com/offer/609060377631.html
2. 登录 1688 账号
3. 按 F12 打开开发者工具
4. 在 Console 输入：`document.cookie`
5. 复制输出内容，保存到 `cookies.json`

#### 方式 2：使用浏览器自动化登录（需要配置）

修改脚本，添加扫码登录功能。

---

### 后续运行

登录一次后，Cookies 会保存，后续直接运行即可：

```bash
python3 auto-fetch-1688.py
```

---

## 添加更多商品

编辑 `auto-fetch-1688.py`，修改 `PRODUCT_URLS` 列表：

```python
PRODUCT_URLS = [
    "https://detail.1688.com/offer/609060377631.html",
    "https://detail.1688.com/offer/xxxxxxxxx.html",  # 添加新商品
    "https://detail.1688.com/offer/xxxxxxxxx.html",
]
```

---

## 定时任务（可选）

设置每天凌晨 2 点自动更新：

```bash
crontab -e
```

添加：
```
0 2 * * * cd /home/admin/.openclaw/workspace/zhaiqu-website && python3 auto-fetch-1688.py >> auto-fetch.log 2>&1
```

---

## 依赖

- Python 3.8+
- Playwright

安装依赖：
```bash
pip3 install playwright --break-system-packages
python3 -m playwright install chromium
```

---

## 输出

运行后会：
1. 抓取商品信息 → `products.json`
2. 生成网站 HTML → `index.html`
3. 自动提交到 GitHub → 网站自动更新

---

## 注意事项

1. 1688 有反爬机制，建议不要频繁抓取（每小时最多 1 次）
2. Cookies 会过期，定期重新登录
3. 如果抓取失败，检查网络连接
