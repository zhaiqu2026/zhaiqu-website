# 1688 数据自动化方案

## 当前问题

1688 网站有严格的反爬机制：
- 需要登录才能查看详细信息
- 检测到爬虫会返回 "Access denied"
- 有验证码和 IP 限制

## 解决方案

### 方案 A：手动导入（立即可用）✅

**步骤：**

1. 创建产品数据模板
```bash
cd /home/admin/.openclaw/workspace/zhaiqu-website
python3 import-products.py template
```

2. 编辑 `products-template.json`，填入产品信息：
```json
[
  {
    "url": "https://detail.1688.com/offer/609060377631.html",
    "title": "阿罗裤 男士平角内裤",
    "price": "¥10.50-15.00",
    "images": [
      "https://cbu01.alicdn.com/img/ibank/O1CN01xxx_!!xxx.jpg"
    ],
    "description": "纯棉材质，舒适透气",
    "company": "深圳市 XXX 服装厂"
  }
]
```

3. 导入并更新网站
```bash
python3 import-products.py products-template.json
```

**优点：**
- 立即可用
- 稳定可靠
- 数据准确

**缺点：**
- 需要手动复制信息（约 5 分钟/商品）

---

### 方案 B：1688 开放平台 API（长期方案）🔧

**申请流程：**

1. 注册 1688 开放平台账号
   - 访问：https://open.1688.com/
   - 用您的 1688 账号登录

2. 创建应用
   - 进入：https://open.1688.com/dev/support.htm
   - 点击"创建应用"
   - 填写应用信息（个人开发者即可）

3. 获取 API Key
   - App Key
   - App Secret

4. 申请 API 权限
   - 商品 API：`alibaba.product.get`
   - 需要提交使用说明

**时间：** 1-3 个工作日审核

**费用：** 基础 API 免费，高级功能收费

**API 文档：**
- 商品详情：https://open.1688.com/api/apidocdetail.htm?aopApiCategory=product_new
- 商品搜索：https://open.1688.com/api/apidocdetail.htm?id=cn.alibaba.open:alibaba.product.search-1

---

### 方案 C：浏览器扩展辅助（折中方案）🔌

我可以帮您写一个浏览器扩展，在浏览 1688 时自动提取商品信息并导出。

**流程：**
1. 安装浏览器扩展（Chrome/Edge）
2. 正常浏览 1688 商品页面
3. 点击扩展按钮，自动提取当前商品信息
4. 导出为 JSON 文件
5. 用 `import-products.py` 导入

**优点：**
- 不需要 API 审核
- 比纯手动快
- 数据准确

**缺点：**
- 需要您手动浏览每个商品页面

---

## 我的建议

**短期（今天）：** 用方案 A，先导入 3-5 个主打产品，让网站有内容展示

**中期（本周）：** 申请 1688 API，或者用方案 C 的浏览器扩展

**长期：** API 自动同步，完全自动化

---

## 快速开始

现在就用方案 A 导入第一批产品：

```bash
cd /home/admin/.openclaw/workspace/zhaiqu-website
python3 import-products.py template
```

然后编辑 `products-template.json`，填入您的产品信息！

---

## 产品图片获取

1688 图片链接通常长这样：
```
https://cbu01.alicdn.com/img/ibank/O1CN01xxxxxxxx_!!xxxxxxxxx.jpg
```

**如何获取：**
1. 打开商品页面
2. 右键产品图片 → 复制图片地址
3. 粘贴到 JSON 文件的 `images` 数组中

可以放多张图片：
```json
"images": [
  "https://cbu01.alicdn.com/img/ibank/O1CN01xxx_!!xxx-1.jpg",
  "https://cbu01.alicdn.com/img/ibank/O1CN01xxx_!!xxx-2.jpg",
  "https://cbu01.alicdn.com/img/ibank/O1CN01xxx_!!xxx-3.jpg"
]
```
