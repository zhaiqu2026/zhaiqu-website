#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 商品自动抓取脚本 - 增强版
使用 stealth 模式绕过反爬
"""

import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
WEBSITE_DIR = Path("/home/admin/.openclaw/workspace/zhaiqu-website")
DATA_FILE = WEBSITE_DIR / "products.json"
COOKIES_FILE = WEBSITE_DIR / "cookies.json"

# 要抓取的商品链接列表（可以从命令行参数或配置文件读取）
DEFAULT_URLS = [
    "https://detail.1688.com/offer/609060377631.html",
]

def fetch_product_info(url, context, cookies=None):
    """抓取单个商品信息（增强版）"""
    print(f"\n🔍 正在抓取：{url}")
    
    page = context.new_page()
    
    try:
        # 如果有 Cookies，先设置
        if cookies:
            context.add_cookies(cookies)
        
        # 设置更真实的 User-Agent 和 Headers
        context.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # 访问页面
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 等待页面完全加载
        page.wait_for_timeout(8000)
        
        # 检查是否被拦截
        page_content = page.content()
        if "Access denied" in page_content or "访问被拒绝" in page_content:
            print(f"  ⚠️  页面被拦截（Access denied）")
            # 尝试滚动页面触发加载
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(3000)
        
        # 尝试提取商品信息
        product_info = {
            "url": url,
            "title": "",
            "price": "",
            "images": [],
            "description": "",
            "company": ""
        }
        
        # 提取标题 - 多种选择器
        title_selectors = [
            "h.d-title",
            "h1",
            ".title",
            "[data-title]"
        ]
        for selector in title_selectors:
            try:
                title = page.query_selector(selector)
                if title:
                    text = title.inner_text().strip()
                    if text and len(text) > 5 and "access" not in text.lower():
                        product_info["title"] = text[:100]
                        break
            except:
                continue
        
        # 提取价格
        price_selectors = [
            ".price-content",
            ".price",
            "[data-price]",
            ".dt-price",
            ".r-price"
        ]
        for selector in price_selectors:
            try:
                price = page.query_selector(selector)
                if price:
                    text = price.inner_text().strip()
                    if text:
                        product_info["price"] = text
                        break
            except:
                continue
        
        # 提取图片 - 更智能的筛选
        try:
            images = page.query_selector_all("img")
            for img in images[:20]:
                src = img.get_attribute("src")
                if src and src.startswith("http") and ("alicdn" in src or "1688" in src):
                    # 过滤掉小图和图标
                    if not any(x in src for x in ["favicon", "icon", "avatar", "logo"]):
                        if src not in product_info["images"]:
                            product_info["images"].append(src)
                            if len(product_info["images"]) >= 5:
                                break
        except Exception as e:
            print(f"  ⚠️  图片提取失败")
        
        # 提取公司名
        try:
            company = page.query_selector(".company-name, .seller-name, .shop-name")
            if company:
                product_info["company"] = company.inner_text().strip()
        except Exception as e:
            print(f"  ⚠️  公司名提取失败")
        
        # 如果什么都没抓到，尝试获取页面标题
        if not product_info["title"]:
            try:
                page_title = page.title()
                if page_title and "access" not in page_title.lower():
                    product_info["title"] = page_title[:100]
            except:
                pass
        
        # 保存 Cookies 供下次使用
        try:
            saved_cookies = context.cookies()
            if saved_cookies:
                with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(saved_cookies, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        if product_info["title"] or product_info["images"]:
            print(f"  ✅ 抓取成功：{product_info['title'][:50] if product_info['title'] else '有图片'}")
        else:
            print(f"  ⚠️  未抓取到有效信息")
        
        return product_info
        
    except Exception as e:
        print(f"  ❌ 抓取失败：{str(e)[:100]}")
        return None
    finally:
        page.close()

def generate_website_html(products):
    """生成网站 HTML"""
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>宅趣网站 - 产品展示</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; padding: 40px 0; }
        .product-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { width: 100%; height: 250px; object-fit: cover; background: #f0f0f0; }
        .product-info { padding: 20px; }
        .product-title { font-size: 1.2em; margin-bottom: 10px; color: #333; }
        .product-price { color: #e74c3c; font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }
        .product-desc { color: #666; font-size: 0.9em; line-height: 1.6; }
        .footer { text-align: center; padding: 30px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 宅趣网站</h1>
        <p>专业代工 · 品质保证</p>
    </div>
    
    <div class="container">
        <div class="products">
"""
    
    if not products:
        html += """
            <div style="grid-column: 1/-1; text-align: center; padding: 60px;">
                <h2>📦 产品数据加载中...</h2>
                <p>请稍后再来查看</p>
            </div>
"""
    else:
        for p in products:
            image = p.get('images', [''])[0] if p.get('images') else ''
            html += f"""
            <div class="product-card">
                <img src="{image}" alt="{p.get('title', '产品')}" class="product-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22250%22%3E%3Crect fill=%22%23f0f0f0%22 width=%22300%22 height=%22250%22/%3E%3Ctext fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22%3E暂无图片%3C/text%3E%3C/svg%3E'">
                <div class="product-info">
                    <h3 class="product-title">{p.get('title', '未命名产品')}</h3>
                    <div class="product-price">{p.get('price', '面议')}</div>
                    <p class="product-desc">{p.get('company', '')}</p>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <div class="footer">
        <p>© 2026 宅趣网站 · 专业代工服务</p>
    </div>
</body>
</html>
"""
    return html

def main(urls=None):
    """主函数"""
    print("🚀 开始抓取 1688 商品信息...")
    
    if urls is None:
        urls = DEFAULT_URLS
    
    products = []
    
    # 加载已有产品
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            existing_urls = {p.get('url') for p in existing}
            products = existing
            print(f"📋 已加载 {len(existing)} 个已有产品")
    
    # 加载 Cookies
    cookies = None
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            print(f"🍪 加载已保存的 Cookies")
    
    with sync_playwright() as p:
        # 启动浏览器（更真实的配置）
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 抓取每个商品
        for i, url in enumerate(urls):
            # 跳过已抓取的商品
            if url in {p.get('url') for p in products}:
                print(f"\n⏭️  跳过已抓取：{url}")
                continue
            
            info = fetch_product_info(url, context, cookies)
            if info:
                products.append(info)
            
            # 请求间隔，避免被封
            if i < len(urls) - 1:
                print("⏱️  等待 5 秒...")
                time.sleep(5)
        
        browser.close()
    
    # 保存产品数据
    if products:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 产品数据已保存到 {DATA_FILE}")
    
    # 生成网站 HTML
    html = generate_website_html(products)
    html_file = WEBSITE_DIR / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 网站 HTML 已更新到 {html_file}")
    
    print(f"\n📊 本次抓取完成：共 {len(products)} 个商品")
    
    # 如果有新商品，自动提交到 GitHub
    if len(products) > 0:
        print("\n🔄 准备自动提交到 GitHub...")
        os.system(f"cd {WEBSITE_DIR} && git add . && git commit -m '自动更新：{len(products)} 个商品' && git push origin main")
        print("✅ 已推送到 GitHub，网站将自动更新！")

if __name__ == "__main__":
    # 从命令行参数读取 URL
    urls = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_URLS
    main(urls)
